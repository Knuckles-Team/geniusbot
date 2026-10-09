"""Tests for the packaging-manifest console entry point (GENIUSBOT-CLIENT-R012.2)."""

import pytest

from geniusbot.services.packaging_cli import check, main
from geniusbot.services.packaging_manifest import PackagingManifestError


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R012.2")
def test_check_validates_default_targets():
    manifest = check()
    names = [target.name for target in manifest.targets]
    assert "console_entry_point" in names
    assert "linux_desktop_entry" in names


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R012.2")
def test_check_rejects_incomplete_targets():
    with pytest.raises(PackagingManifestError):
        check(
            raw_targets=[
                {
                    "name": "console_entry_point",
                    "build_tool": "setuptools",
                    "output_path": "dist/geniusbot",
                }
            ]
        )


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R012.2")
def test_main_check_prints_build_plan(capsys):
    exit_code = main(["--check"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "packaging manifest valid" in out
    assert "console_entry_point" in out


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R012.2")
def test_main_without_check_prints_help_and_fails(capsys):
    exit_code = main([])
    assert exit_code == 1
