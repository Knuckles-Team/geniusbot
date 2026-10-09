"""Tests for the typed packaging-manifest model (GENIUSBOT-CLIENT-R012.1)."""

import pytest

from geniusbot.services.packaging_manifest import (
    PackagingManifestError,
    build_manifest,
)


def _complete_targets(version="1.2.3"):
    return [
        {"name": "console_entry_point", "build_tool": "pip", "output_path": "dist/geniusbot", "version": version},
        {
            "name": "onefile_executable",
            "build_tool": "pyinstaller",
            "output_path": "dist/geniusbot.exe",
            "version": version,
        },
        {
            "name": "windows_installer",
            "build_tool": "inno-setup",
            "output_path": "dist/geniusbot-setup.exe",
            "version": version,
        },
        {
            "name": "linux_desktop_entry",
            "build_tool": "desktop-file-utils",
            "output_path": "dist/geniusbot.desktop",
            "version": version,
        },
    ]


def test_complete_manifest_accepted():
    manifest = build_manifest("1.2.3", _complete_targets())
    assert manifest.target("onefile_executable").build_tool == "pyinstaller"


def test_rejects_missing_target():
    targets = [t for t in _complete_targets() if t["name"] != "windows_installer"]
    with pytest.raises(PackagingManifestError):
        build_manifest("1.2.3", targets)


def test_rejects_empty_source_version():
    with pytest.raises(PackagingManifestError):
        build_manifest("", _complete_targets())


def test_rejects_version_mismatch():
    targets = _complete_targets()
    targets[0]["version"] = "9.9.9"
    with pytest.raises(PackagingManifestError):
        build_manifest("1.2.3", targets)


def test_rejects_duplicate_target_names():
    targets = _complete_targets() + [_complete_targets()[0]]
    with pytest.raises(PackagingManifestError):
        build_manifest("1.2.3", targets)


def test_rejects_missing_field():
    with pytest.raises(PackagingManifestError):
        build_manifest("1.2.3", [{"name": "console_entry_point"}])


def test_target_lookup_rejects_unknown_name():
    manifest = build_manifest("1.2.3", _complete_targets())
    with pytest.raises(PackagingManifestError):
        manifest.target("macos_dmg")
