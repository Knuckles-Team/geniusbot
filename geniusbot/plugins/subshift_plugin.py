#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("..")

from PyQt5.QtWidgets import (
    QGridLayout,
    QPushButton,
    QSpinBox,
    QLabel,
    QHBoxLayout, QWidget, QFileDialog
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
import pkg_resources
package = 'subshift'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    import subshift
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class SubshiftTab(QWidget):
    def __init__(self, console):
        super(SubshiftTab, self).__init__()
        self.subshift_tab = QWidget()
        self.console = console

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

        self.subshift_tab.setLayout(layout)

    def check_subtitle_seconds(self):
        if self.sub_time_spin_box.value() > 0:
            self.shift_subtitle_button.setEnabled(True)
        elif self.sub_time_spin_box.value() == 0:
            self.shift_subtitle_button.setEnabled(False)
        else:
            self.shift_subtitle_button.setEnabled(True)

    def shift_subtitle(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Shifting Subtitles...\n")
        self.subshift_thread = QThread()
        if self.sub_time_spin_box.value() > 0:
            mode = "+"
        else:
            mode = "-"
        time = abs(self.sub_time_spin_box.value())
        self.subshift_worker = SubshiftWorker(self.open_subtitlefile_label.text(), mode, time)
        self.subshift_worker.moveToThread(self.subshift_thread)
        self.subshift_thread.started.connect(self.subshift_worker.run)
        self.subshift_worker.finished.connect(self.subshift_thread.quit)
        self.subshift_worker.finished.connect(self.subshift_worker.deleteLater)
        self.subshift_thread.finished.connect(self.subshift_thread.deleteLater)
        self.subshift_worker.progress.connect(self.report_web_progress_bar)
        self.subshift_thread.start()
        self.shift_subtitle_button.setEnabled(False)
        self.subshift_thread.finished.connect(
            lambda: self.shift_subtitle_button.setEnabled(True)
        )
        self.subshift_thread.finished.connect(
            lambda: self.refresh_subtitlefile()
        )
        self.console.setText(f"[Genius Bot] Subtitle Shift Completed!\n")

    def refresh_subtitlefile(self):
        with open(self.open_subtitlefile_label.text(), 'r') as file:
            self.subtitles = file.read()
        self.subtitles = self.subtitles + self.subtitle_label.text()
        self.subtitles = self.subtitles.strip()
        self.subtitle_label.setText(self.subtitles)

    def open_subtitlefile(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening Subtitle file\n")
        self.subtitle_label.setText("")
        subtitle_file_name = QFileDialog.getOpenFileName(self, 'Subtitle File')
        print(subtitle_file_name[0])
        self.open_subtitlefile_label.setText(subtitle_file_name[0])
        with open(subtitle_file_name[0], 'r') as file:
            self.subtitles = file.read()
        self.subtitles = self.subtitles + self.subtitle_label.text()
        self.subtitles = self.subtitles.strip()
        self.subtitle_label.setText(self.subtitles)


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
