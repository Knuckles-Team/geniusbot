#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
import subshift
from PyQt5.QtWidgets import (
    QGridLayout,
    QPushButton,
    QSpinBox,
    QWidget,
    QLabel,
    QHBoxLayout
)
from PyQt5.QtCore import QObject, pyqtSignal
from qt.colors import yellow, green, orange, blue, red, purple
from qt.scrollable_widget import ScrollLabel


def subshift_tab(self):
    self.open_subtitlefile_button = QPushButton("Open File")
    self.open_subtitlefile_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
    self.open_subtitlefile_button.clicked.connect(self.open_subtitlefile)
    self.shift_subtitle_button = QPushButton("Shift Subtitles ↹")
    self.shift_subtitle_button.setStyleSheet(
        f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
    self.shift_subtitle_button.clicked.connect(self.shift_subtitle)

    # self.subtitle_label = QLabel(self)
    self.subtitle_label = ScrollLabel(self)
    self.subtitle_label.hide()
    self.subtitle_label.setText(f"Subtitle file contents will be shown here\n")
    self.subtitle_label.setFont("Arial")
    self.subtitle_label.setFontColor(background_color="white", color="black")
    self.subtitle_label.setScrollWheel("Top")
    self.subtitle_menu_widget = QWidget(self)
    menu_layout = QHBoxLayout()
    self.open_subtitlefile_label = QLabel("None")
    self.shift_time_label = QLabel("Shift Time")
    self.sub_time_spin_box = QSpinBox(self)
    self.sub_time_spin_box.setRange(-2147483646, 2147483646)
    self.sub_time_spin_box.setValue(0)
    self.sub_time_spin_box.valueChanged.connect(self.check_subtitle_seconds)
    self.shift_subtitle_button.setEnabled(False)
    layout = QGridLayout()
    menu_layout.addWidget(self.shift_time_label)
    menu_layout.addWidget(self.sub_time_spin_box)
    menu_layout.addWidget(self.open_subtitlefile_button)
    menu_layout.addWidget(self.open_subtitlefile_label)
    menu_layout.setStretch(0, 1)
    menu_layout.setStretch(1, 1)
    menu_layout.setStretch(2, 3)
    menu_layout.setStretch(3, 24)

    self.subtitle_menu_widget.setLayout(menu_layout)
    layout.addWidget(self.subtitle_menu_widget, 0, 0, 1, 1)
    layout.addWidget(self.shift_subtitle_button, 2, 0, 1, 1)
    layout.addWidget(self.subtitle_label, 3, 0, 1, 1)
    self.tab_widget.setTabText(4, "Shift Subtitles")
    self.tab5.setLayout(layout)


class SubshiftWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, subtitle_file, mode, time):
        super().__init__()
        self.subtitle_file = subtitle_file
        self.mode = mode
        self.time = time

    def run(self):
        """Long-running task."""
        print(f"Subtitle {self.subtitle_file} was shifted {self.mode}{self.time}")
        subshift.subshift([f"-f", f"{self.subtitle_file}", f"-m", f"{self.mode}", f"-t", f"{self.time}"])
        self.progress.emit(100)
        self.finished.emit()
