"""Typed model and validator for the installed generated Graph OS operation registry.

Implements the `.1` slice of GENIUSBOT-CLIENT-R002: a typed registry-entry model plus a
validator that refuses a malformed entry or digest before the entry can be used to
authorize any network call. The `.2` slice (wiring this into the gateway client's
pre-call check) is tracked separately.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
        raise OperationRegistryError(f"digest for {entry.operation!r} must be a non-empty string")
    digest = entry.digest.lower()
    if len(digest) != 64 or not set(digest) <= _HEX_DIGITS:
        raise OperationRegistryError(f"digest for {entry.operation!r} is not a valid sha256 hex digest")
    if not isinstance(entry.method, str) or entry.method.upper() not in _VALID_METHODS:
        raise OperationRegistryError(f"unsupported method {entry.method!r} for operation {entry.operation!r}")


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
            raise OperationRegistryError(f"registry entry missing required field: {exc}") from exc
        if entry.operation in entries:
            raise OperationRegistryError(f"duplicate operation in registry: {entry.operation!r}")
        entries[entry.operation] = entry
    return OperationRegistry(entries=entries)
