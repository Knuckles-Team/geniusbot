import sys

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Share a single QApplication instance cross-tests to prevent multiple instantiation crashes."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app
