"""Typed model and validator for the installed generated Graph OS operation registry.

Implements the `.1` slice of GENIUSBOT-CLIENT-R002: a typed registry-entry model plus a
validator that refuses a malformed entry or digest before the entry can be used to
authorize any network call. The `.2` slice adds `load_installed_registry`, which reads
the installed generated registry file from disk and refuses to start the application
if it is missing, unparsable, or fails `build_registry` validation.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

_DEFAULT_REGISTRY_FILENAME = "operation_registry.json"
_REGISTRY_PATH_ENV_VAR = "GENIUSBOT_OPERATION_REGISTRY_PATH"

_VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_HEX_DIGITS = set("0123456789abcdef")


class OperationRegistryError(ValueError):
    """Raised when a registry entry, digest, or registry-wide invariant is malformed."""


@dataclass(frozen=True)
class OperationRegistryEntry:
    """One operation entry from the installed generated operation registry."""

    operation: str
    digest: str
    method: str = "POST"

    def __post_init__(self) -> None:
        validate_registry_entry(self)


def validate_registry_entry(entry: OperationRegistryEntry) -> None:
    """Validate a single registry entry, raising OperationRegistryError on failure."""
    if not isinstance(entry.operation, str) or not entry.operation.strip():
        raise OperationRegistryError("operation name must be a non-empty string")
    if not isinstance(entry.digest, str) or not entry.digest:
        raise OperationRegistryError(
            f"digest for {entry.operation!r} must be a non-empty string"
        )
    digest = entry.digest.lower()
    if len(digest) != 64 or not set(digest) <= _HEX_DIGITS:
        raise OperationRegistryError(
            f"digest for {entry.operation!r} is not a valid sha256 hex digest"
        )
    if not isinstance(entry.method, str) or entry.method.upper() not in _VALID_METHODS:
        raise OperationRegistryError(
            f"unsupported method {entry.method!r} for operation {entry.operation!r}"
        )


@dataclass(frozen=True)
class OperationRegistry:
    """A validated, de-duplicated mapping of operation name to its registry entry."""

    entries: dict[str, OperationRegistryEntry] = field(default_factory=dict)

    def lookup(self, operation: str) -> OperationRegistryEntry:
        """Return the entry for `operation`, raising OperationRegistryError if unknown."""
        try:
            return self.entries[operation]
        except KeyError as exc:
            raise OperationRegistryError(f"unknown operation: {operation!r}") from exc

    def validate_digest(self, operation: str, digest: str) -> None:
        """Raise OperationRegistryError if `digest` does not match the installed entry."""
        entry = self.lookup(operation)
        if entry.digest.lower() != digest.lower():
            raise OperationRegistryError(f"digest mismatch for operation {operation!r}")


def build_registry(raw_entries: list[dict]) -> OperationRegistry:
    """Build a validated OperationRegistry from raw dict entries.

    Raises OperationRegistryError on any malformed entry, missing field, or duplicate
    operation name, before the registry can be considered installed.
    """
    entries: dict[str, OperationRegistryEntry] = {}
    for raw in raw_entries:
        try:
            entry = OperationRegistryEntry(
                operation=raw["operation"],
                digest=raw["digest"],
                method=raw.get("method", "POST"),
            )
        except KeyError as exc:
            raise OperationRegistryError(
                f"registry entry missing required field: {exc}"
            ) from exc
        if entry.operation in entries:
            raise OperationRegistryError(
                f"duplicate operation in registry: {entry.operation!r}"
            )
        entries[entry.operation] = entry
    return OperationRegistry(entries=entries)


def installed_registry_path() -> str:
    """Return the path to the installed generated operation registry file.

    `GENIUSBOT_OPERATION_REGISTRY_PATH` overrides the default, which is the generated
    registry file installed alongside this module.
    """
    override = os.environ.get(_REGISTRY_PATH_ENV_VAR)
    if override:
        return override
    return os.path.join(os.path.dirname(__file__), _DEFAULT_REGISTRY_FILENAME)


def load_installed_registry(path: str | None = None) -> OperationRegistry:
    """Load and validate the installed generated operation registry from disk.

    This is the real startup-path entry point for R002.2: it is called before the
    application window is constructed, so a missing file, unparsable JSON, a JSON
    body that is not a list, or any entry/duplicate failure from `build_registry`
    raises `OperationRegistryError` and refuses to start the application.
    """
    registry_path = path if path is not None else installed_registry_path()
    try:
        with open(registry_path, encoding="utf-8") as handle:
            raw = json.load(handle)
    except FileNotFoundError as exc:
        raise OperationRegistryError(
            f"installed operation registry not found: {registry_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise OperationRegistryError(
            f"installed operation registry is not valid JSON: {registry_path}"
        ) from exc
    if not isinstance(raw, list):
        raise OperationRegistryError(
            f"installed operation registry must be a JSON list of entries: {registry_path}"
        )
    return build_registry(raw)
