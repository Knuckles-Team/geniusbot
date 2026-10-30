"""Display branding must not change installation identity."""

import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.spec("AXIL-CLIENT-R012")
class PackagingDisplayIdentityTests(unittest.TestCase):
    def test_linux_display_name_preserves_launcher_identity(self):
        entry = (ROOT / "packaging/linux/axil.desktop").read_text()
        for line in ("Name=Axil", "Exec=/usr/bin/axil", "Icon=axil"):
            self.assertIn(line, entry.splitlines())
        control = (ROOT / "packaging/linux/control").read_text()
        self.assertIn("Package: axil", control.splitlines())
        self.assertIn("Description: Axil desktop GUI for Arbora", control.splitlines())

    def test_windows_display_name_preserves_installation_identity(self):
        installer = (ROOT / "packaging/windows/setup.iss").read_text()
        for line in (
            '#define MyAppName "Axil"',
            '#define MyAppExeName "axil.exe"',
            "AppId={{40E3E132-1207-4128-80CF-8B31B308E2C9}",
            r"DefaultDirName={autopf}\Axil",
            "OutputBaseFilename=axil-setup-x64",
        ):
            self.assertIn(line, installer.splitlines())


if __name__ == "__main__":
    unittest.main()
