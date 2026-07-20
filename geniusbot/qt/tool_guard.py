import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from geniusbot.qt.colors import (
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    BG_PRIMARY,
    BG_SECONDARY,
    BORDER_COLOR,
    TEXT_MAIN,
)


class ToolGuardDialog(QDialog):
    """Polished, space-dark mode tool authorization dialog (CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox/OS-5.5)."""

    def __init__(self, tool_name: str, arguments: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Action Authorization Required")
        self.setMinimumSize(450, 300)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        # Style the dialog
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {BG_PRIMARY};
                border: 2px solid {ACCENT_PRIMARY};
                border-radius: 12px;
            }}
            QLabel {{
                color: {TEXT_MAIN};
                font-family: "Outfit", "Inter", sans-serif;
            }}
        """
        )

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        title_label = QLabel("🛡️ Secure Tool Execution Guard")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7C4DFF;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            f"An agent wants to execute the following tool: <b>{tool_name}</b>"
        )
        desc_label.setStyleSheet("font-size: 13px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Arguments JSON Viewer
        layout.addWidget(QLabel("Arguments:"))
        self.args_viewer = QTextEdit()
        self.args_viewer.setReadOnly(True)
        try:
            formatted_json = json.dumps(arguments, indent=4)
        except Exception:
            formatted_json = str(arguments)
        self.args_viewer.setPlainText(formatted_json)
        self.args_viewer.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                font-family: "Cascadia Code", "Fira Code", monospace;
                font-size: 12px;
                color: #A9B2C3;
            }}
        """
        )
        layout.addWidget(self.args_viewer)

        # Prompt Injection warning if any warning exists in the query/arguments
        self.warning_label = QLabel(
            "⚠️ Verify that parameters are safe before approving."
        )
        self.warning_label.setStyleSheet("color: #FFD740; font-size: 11px;")
        layout.addWidget(self.warning_label)

        # Horizontal layout for approval buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Reject button (Red)
        self.btn_reject = QPushButton("Reject Run")
        self.btn_reject.setStyleSheet(
            """
            QPushButton {
                background-color: #FF5252;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """
        )
        self.btn_reject.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_reject)

        # Approve button (Success Green)
        self.btn_approve = QPushButton("Authorize Action")
        self.btn_approve.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ACCENT_SUCCESS};
                color: {BG_PRIMARY};
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #00C853;
            }}
        """
        )
        self.btn_approve.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_approve)

        layout.addLayout(button_layout)
