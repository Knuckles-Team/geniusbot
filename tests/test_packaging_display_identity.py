"""Display branding must not change installation identity."""

import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.spec("GENIUSBOT-CLIENT-R012")
class PackagingDisplayIdentityTests(unittest.TestCase):
    def test_linux_display_name_preserves_launcher_identity(self):
        entry = (ROOT / "packaging/linux/geniusbot.desktop").read_text()
        for line in ("Name=Axil Desk", "Exec=/usr/bin/geniusbot", "Icon=geniusbot"):
            self.assertIn(line, entry.splitlines())
        control = (ROOT / "packaging/linux/control").read_text()
        self.assertIn("Package: geniusbot", control.splitlines())
        self.assertIn(
            "Description: Axil Desk desktop GUI for Arbora", control.splitlines()
        )

    def test_windows_display_name_preserves_installation_identity(self):
        installer = (ROOT / "packaging/windows/setup.iss").read_text()
        for line in (
            '#define MyAppName "Axil Desk"',
            '#define MyAppExeName "geniusbot.exe"',
            "AppId={{40E3E132-1207-4128-80CF-8B31B308E2C9}",
            r"DefaultDirName={autopf}\Geniusbot",
            "OutputBaseFilename=geniusbot-setup-x64",
        ):
            self.assertIn(line, installer.splitlines())


if __name__ == "__main__":
    unittest.main()
