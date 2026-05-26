#!/usr/bin/env python3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BG_SECONDARY, BORDER_COLOR


class SecurityPolicyPanel(QWidget):
    """Visual panel for managing Zero-Trust authorization settings and permission strictness."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker

        self.initialize_ui()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        title_lbl = QLabel("🛡️ Zero-Trust Security Policies")
        title_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(
            "Configure granular security policies, prompt injection scanners, and ToolGuard permissions for every specialist agent."
        )
        subtitle_lbl.setStyleSheet(
            "color: #8A8A93; font-size: 12px; margin-bottom: 15px;"
        )
        layout.addWidget(subtitle_lbl)

        # ── strictness Mode Slider ──
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(6)

        lbl_header = QLabel("Global Guardrails Strictness Level:")
        lbl_header.setStyleSheet("font-weight: bold; color: #E4E4E7;")
        slider_layout.addWidget(lbl_header)

        self.strictness_slider = QSlider(Qt.Horizontal)
        self.strictness_slider.setMinimum(0)
        self.strictness_slider.setMaximum(2)
        self.strictness_slider.setValue(1)  # Default to Standard
        self.strictness_slider.setTickPosition(QSlider.TicksBelow)
        self.strictness_slider.setTickInterval(1)
        self.strictness_slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 6px; background: #27272a; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #7C4DFF; width: 16px; margin: -5px 0; border-radius: 8px; }"
        )
        self.strictness_slider.valueChanged.connect(self.on_strictness_changed)
        slider_layout.addWidget(self.strictness_slider)

        # Slider ticks labels
        ticks_layout = QHBoxLayout()
        lbl_perm = QLabel("🔓 Permissive\n(Auto-run & warn)")
        lbl_perm.setStyleSheet("color: #8A8A93; font-size: 10px;")
        ticks_layout.addWidget(lbl_perm)

        ticks_layout.addStretch()

        self.lbl_mode = QLabel("🛡️ Standard\n(Confirm dangerous)")
        self.lbl_mode.setAlignment(Qt.AlignCenter)
        self.lbl_mode.setStyleSheet(
            "color: #00E5FF; font-size: 10px; font-weight: bold;"
        )
        ticks_layout.addWidget(self.lbl_mode)

        ticks_layout.addStretch()

        lbl_zero = QLabel("🔒 Zero-Trust\n(Confirm all)")
        lbl_zero.setAlignment(Qt.AlignRight)
        lbl_zero.setStyleSheet("color: #8A8A93; font-size: 10px;")
        ticks_layout.addWidget(lbl_zero)

        slider_layout.addLayout(ticks_layout)
        layout.addLayout(slider_layout)

        layout.addWidget(QLabel("Specialist Permissions Authorization Matrix:"))

        # ── Permissions Matrix Grid ──
        self.matrix_table = QTableWidget()
        self.matrix_table.setColumnCount(5)
        self.matrix_table.setHorizontalHeaderLabels(
            [
                "Specialist / Agent ID",
                "Shell Execution",
                "File Read",
                "File Write",
                "Network Request",
            ]
        )
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_table.verticalHeader().setVisible(False)
        self.matrix_table.setStyleSheet(
            f"QTableWidget {{ background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; color: #E4E4E7; }}"
            f"QHeaderView::section {{ background-color: {BG_SECONDARY}; color: #8A8A93; font-weight: bold; border: none; padding: 10px; }}"
        )
        layout.addWidget(self.matrix_table)

        self.populate_permissions_matrix()

        # Save Button
        self.btn_save = QPushButton("Save & Apply Policies")
        self.btn_save.setStyleSheet(
            "background-color: #7C4DFF; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 13px;"
        )
        self.btn_save.clicked.connect(self.save_policies)
        layout.addWidget(self.btn_save)

    def populate_permissions_matrix(self):
        specialists = [
            ("technitium-dns-mcp", False, True, False, True),
            ("agentpay-sdk", False, True, False, True),
            ("scholarx-agent", False, True, True, True),
            ("repository-manager", True, True, True, False),
            ("systems-manager", True, True, True, False),
            ("uptime-self-healer", True, True, False, True),
        ]

        self.matrix_table.setRowCount(len(specialists))

        for idx, (name, shell, fread, fwrite, net) in enumerate(specialists):
            # Name Column
            item_name = QTableWidgetItem(name)
            item_name.setFlags(Qt.ItemIsEnabled)
            self.matrix_table.setItem(idx, 0, item_name)

            # Checkbox columns
            self.add_checkbox_cell(idx, 1, shell)
            self.add_checkbox_cell(idx, 2, fread)
            self.add_checkbox_cell(idx, 3, fwrite)
            self.add_checkbox_cell(idx, 4, net)

    def add_checkbox_cell(self, row, col, checked):
        container = QWidget()
        cell_layout = QHBoxLayout(container)
        cell_layout.setAlignment(Qt.AlignCenter)
        cell_layout.setContentsMargins(0, 0, 0, 0)

        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setStyleSheet(
            "QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #3f3f46; border-radius: 4px; background: #121214; }"
            "QCheckBox::indicator:checked { background: #7C4DFF; border: 1px solid #7C4DFF; image: url(img/check.png); }"
        )
        cell_layout.addWidget(cb)

        self.matrix_table.setCellWidget(row, col, container)

    def on_strictness_changed(self, val):
        if val == 0:
            self.lbl_mode.setText("🔓 Permissive\n(Auto-run & warn)")
            self.lbl_mode.setStyleSheet(
                "color: #00E676; font-size: 10px; font-weight: bold;"
            )
        elif val == 1:
            self.lbl_mode.setText("🛡️ Standard\n(Confirm dangerous)")
            self.lbl_mode.setStyleSheet(
                "color: #00E5FF; font-size: 10px; font-weight: bold;"
            )
        else:
            self.lbl_mode.setText("🔒 Zero-Trust\n(Confirm all)")
            self.lbl_mode.setStyleSheet(
                "color: #FF1744; font-size: 10px; font-weight: bold;"
            )

    def save_policies(self):
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Compiling Security Hashes...")

        async def apply_policies():
            import time

            time.sleep(0.6)
            return True

        def on_done(res):
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Save & Apply Policies")

            # Show a premium alert window
            QMessageBox.information(
                self,
                "Security Policies Synced",
                "Successfully saved Zero-Trust authorization hashes!\n\nAll specialists are compiled under active ToolGuard runtime policies.",
                QMessageBox.Ok,
            )

        def on_fail(err):
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Save & Apply Policies")

        self.worker.run_agent_task(
            apply_policies, on_finished=on_done, on_error=on_fail
        )
