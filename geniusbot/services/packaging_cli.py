"""Console entry point for validating the cross-platform packaging manifest.

Implements the `.2` slice of GENIUSBOT-CLIENT-R012: `geniusbot-package --check` builds
the packaging manifest definition with `build_manifest` and prints the build plan if
it is valid. No PyInstaller, Inno Setup, or desktop-entry build is invoked here.
"""

from __future__ import annotations

import argparse
import sys

from geniusbot import __version__
from geniusbot.services.packaging_manifest import (
    PackagingManifest,
    PackagingManifestError,
    build_manifest,
)


def default_raw_targets() -> list[dict]:
    """The declared packaging targets built from the same versioned source tree."""
    return [
        {
            "name": "console_entry_point",
            "build_tool": "setuptools",
            "output_path": "dist/geniusbot",
        },
        {
            "name": "onefile_executable",
            "build_tool": "pyinstaller",
            "output_path": "dist/geniusbot-onefile",
        },
        {
            "name": "windows_installer",
            "build_tool": "inno_setup",
            "output_path": "dist/geniusbot-setup.exe",
        },
        {
            "name": "linux_desktop_entry",
            "build_tool": "desktop-file-install",
            "output_path": "packaging/linux/geniusbot.desktop",
        },
    ]


def build_plan_lines(manifest: PackagingManifest) -> list[str]:
    """Render the validated manifest's build plan as printable lines."""
    lines = [f"packaging manifest valid for source_version={manifest.source_version}"]
    for target in manifest.targets:
        lines.append(f"  - {target.name}: {target.build_tool} -> {target.output_path}")
    return lines


def check(
    source_version: str | None = None, raw_targets: list[dict] | None = None
) -> PackagingManifest:
    """Validate the packaging manifest, raising PackagingManifestError if incomplete."""
    version = source_version if source_version is not None else __version__
    targets = raw_targets if raw_targets is not None else default_raw_targets()
    return build_manifest(version, targets)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="geniusbot-package")
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the packaging manifest and print the build plan",
    )
    args = parser.parse_args(argv)

    if not args.check:
        parser.print_help()
        return 1

    try:
        manifest = check()
    except PackagingManifestError as exc:
        print(f"packaging manifest invalid: {exc}", file=sys.stderr)
        return 1

    for line in build_plan_lines(manifest):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
