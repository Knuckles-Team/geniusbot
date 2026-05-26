"""Verify package initialization and version metadata."""

import importlib

import pytest

PKG_NAME = "geniusbot"


@pytest.fixture
def pkg_name():
    return PKG_NAME


def test_package_importable(pkg_name):
    """Package should be importable."""
    mod = importlib.import_module(pkg_name)
    assert mod is not None


def test_version_exists(pkg_name):
    """Package should expose __version__."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    assert version is not None, f"{pkg_name} has no __version__"


def test_version_format(pkg_name):
    """Version should follow semver-like format."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    parts = version.split(".")
    assert len(parts) >= 2, f"Version {version} should have at least major.minor"
