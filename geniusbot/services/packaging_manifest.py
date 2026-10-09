"""Typed model and validator for the cross-platform packaging manifest.

Implements the `.1` slice of GENIUSBOT-CLIENT-R012: a typed packaging manifest model
plus a validator that refuses an incomplete manifest -- one missing a required build
target, a target missing a build tool or output path, or a target whose version does
not match the source tree's declared version. No PyInstaller/Inno Setup/desktop-entry
build is invoked here; the `.2` slice wires an actual build pipeline against a
validated manifest.
"""

from __future__ import annotations

from dataclasses import dataclass, field

REQUIRED_TARGETS = (
    "console_entry_point",
    "onefile_executable",
    "windows_installer",
    "linux_desktop_entry",
)


class PackagingManifestError(ValueError):
    """Raised when a packaging manifest is incomplete or malformed."""


@dataclass(frozen=True)
class PackagingTarget:
    """One packaging build target, built from the same versioned source tree."""

    name: str
    build_tool: str
    output_path: str
    version: str


@dataclass(frozen=True)
class PackagingManifest:
    """The full cross-platform packaging manifest for one versioned source tree."""

    source_version: str
    targets: tuple[PackagingTarget, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_packaging_manifest(self)

    def target(self, name: str) -> PackagingTarget:
        """Return the named target, raising PackagingManifestError if absent."""
        for candidate in self.targets:
            if candidate.name == name:
                return candidate
        raise PackagingManifestError(f"no packaging target named {name!r}")


def validate_packaging_manifest(manifest: PackagingManifest) -> None:
    """Validate a packaging manifest, raising PackagingManifestError if incomplete."""
    if not isinstance(manifest.source_version, str) or not manifest.source_version.strip():
        raise PackagingManifestError("source_version must be a non-empty string")

    names = [target.name for target in manifest.targets]
    if len(names) != len(set(names)):
        raise PackagingManifestError("duplicate packaging target names in manifest")

    missing = [name for name in REQUIRED_TARGETS if name not in names]
    if missing:
        raise PackagingManifestError(f"packaging manifest missing required targets: {missing}")

    for target in manifest.targets:
        if not isinstance(target.build_tool, str) or not target.build_tool.strip():
            raise PackagingManifestError(f"target {target.name!r} missing build_tool")
        if not isinstance(target.output_path, str) or not target.output_path.strip():
            raise PackagingManifestError(f"target {target.name!r} missing output_path")
        if target.version != manifest.source_version:
            raise PackagingManifestError(
                f"target {target.name!r} version {target.version!r} does not match "
                f"source_version {manifest.source_version!r}"
            )


def build_manifest(source_version: str, raw_targets: list[dict]) -> PackagingManifest:
    """Build a validated PackagingManifest from raw target dicts.

    Raises PackagingManifestError on any missing field, missing required target, or
    version mismatch, before the manifest can be considered ready to build from.
    """
    targets = []
    for raw in raw_targets:
        try:
            targets.append(
                PackagingTarget(
                    name=raw["name"],
                    build_tool=raw["build_tool"],
                    output_path=raw["output_path"],
                    version=raw.get("version", source_version),
                )
            )
        except KeyError as exc:
            raise PackagingManifestError(f"packaging target missing required field: {exc}") from exc
    return PackagingManifest(source_version=source_version, targets=tuple(targets))
