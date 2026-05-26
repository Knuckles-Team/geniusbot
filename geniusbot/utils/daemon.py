from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class GeniusBotDaemon(QObject):
    """Cockpit background tray daemon managing window states and quick actions."""

    show_requested = Signal()
    terminal_requested = Signal()
    exit_requested = Signal()
    health_check_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)

        # Set a default elegant icon representation
        # PySide6 can load standard theme icons as fallback
        icon = QIcon.fromTheme("system-run", QIcon.fromTheme("utilities-terminal"))
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("GeniusBot Multi-Agent Cockpit")

        # Context Menu
        self.menu = QMenu()
        self.menu.setStyleSheet(
            """
            QMenu {
                background-color: #1E1E24;
                color: #F5F5F7;
                border: 1px solid #2E2E38;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #7C4DFF;
                color: white;
            }
        """
        )

        # Add Actions
        show_action = QAction("🌌 Show Dashboard", self)
        show_action.triggered.connect(self.show_requested.emit)
        self.menu.addAction(show_action)

        term_action = QAction("🖥️ Quick CLI Terminal", self)
        term_action.triggered.connect(self.terminal_requested.emit)
        self.menu.addAction(term_action)

        health_action = QAction("🛡️ Engine Health Diagnostics", self)
        health_action.triggered.connect(self.health_check_requested.emit)
        self.menu.addAction(health_action)

        self.menu.addSeparator()

        exit_action = QAction("🚪 Exit Cockpit", self)
        exit_action.triggered.connect(self.exit_requested.emit)
        self.menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.menu)

    def start(self):
        """Display the system tray icon."""
        self.tray_icon.show()

    def stop(self):
        """Hide the system tray icon."""
        self.tray_icon.hide()
