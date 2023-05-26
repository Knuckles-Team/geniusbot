#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("..")
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGridLayout,
    QCheckBox
)
from PyQt5.QtCore import QObject, pyqtSignal
from qt.colors import yellow, green, orange, blue, red, purple
from qt.scrollable_widget import ScrollLabel


def media_manager_tab(self):
    media_manager_layout = QGridLayout()
    self.media_manager_media_location_button = QPushButton("Media Location")
    self.media_manager_media_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
    self.media_manager_media_location_button.clicked.connect(self.media_manager_media_location)
    self.media_manager_media_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
    self.media_manager_move_location_button = QPushButton("Move Location")
    self.media_manager_move_location_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
    self.media_manager_move_location_button.clicked.connect(self.media_manager_move_location)
    self.media_manager_move_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
    self.subtitle_ticker = QCheckBox("Apply Subtitles")
    self.move_ticker = QCheckBox("Move Media")
    self.media_manager_files_label = ScrollLabel(self)
    self.media_manager_files_label.hide()
    self.media_manager_files_label.setText(f"Media files found will be shown here\n")
    self.media_manager_files_label.setFont("Arial")
    self.media_manager_files_label.setFontColor(background_color="white", color="black")
    self.media_manager_files_label.setScrollWheel("Top")
    self.media_manager_run_button = QPushButton("Run ⥀")
    self.media_manager_run_button.setStyleSheet(
        f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
    self.media_manager_run_button.clicked.connect(self.manage_media)
    media_manager_layout.addWidget(self.media_manager_media_location_button, 0, 0, 1, 1)
    media_manager_layout.addWidget(self.media_manager_media_location_label, 0, 1, 1, 1)
    media_manager_layout.addWidget(self.media_manager_move_location_button, 1, 0, 1, 1)
    media_manager_layout.addWidget(self.media_manager_move_location_label, 1, 1, 1, 1)
    media_manager_layout.addWidget(self.move_ticker, 2, 0, 1, 1)
    media_manager_layout.addWidget(self.subtitle_ticker, 2, 1, 1, 1)
    media_manager_layout.addWidget(self.media_manager_files_label, 3, 0, 1, 2)
    media_manager_layout.addWidget(self.media_manager_run_button, 4, 0, 1, 2)
    self.tab_widget.setTabText(2, "Media Manager")
    self.tab3.setLayout(media_manager_layout)


class MediaManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, media_manager, directory, move, destination, subtitle):
        super().__init__()
        self.media_manager = media_manager
        self.directory = directory
        self.move = move
        self.destination = destination
        self.subtitle = subtitle

    def run(self):
        """Long-running task."""
        self.media_manager.set_media_directory(media_directory=self.directory)
        self.media_manager.find_media()
        self.media_manager.clean_media(subtitle=self.subtitle)
        if os.path.isdir(os.path.normpath(self.destination)) and self.move is True:
            self.media_manager.move_media(target_directory=self.destination)

        self.progress.emit(100)
        self.finished.emit()
