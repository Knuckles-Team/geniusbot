#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append("..")
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGridLayout,
    QCheckBox, QWidget, QFileDialog
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
    from qt.scrollable_widget import ScrollLabel
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
    from geniusbot.qt.scrollable_widget import ScrollLabel
import pkg_resources
package = 'media-manager'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from media_manager import MediaManager
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class MediaManagerTab(QWidget):
    def __init__(self, console):
        super(MediaManagerTab, self).__init__()
        self.console = console
        self.media_manager = MediaManager()
        self.media_manager_tab = QWidget()
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
        self.media_manager_tab.setLayout(media_manager_layout)

    def manage_media(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media...\n")

        if self.subtitle_ticker.isChecked():
            subtitle_boolean = True
        else:
            subtitle_boolean = False

        if self.move_ticker.isChecked():
            move_boolean = True
        else:
            move_boolean = False

        self.media_manager_thread = QThread()
        self.media_manager_worker = MediaManagerWorker(media_manager=self.media_manager,
                                                       directory=self.media_manager_media_location_label.text(),
                                                       move=move_boolean,
                                                       destination=self.media_manager_move_location_label.text(),
                                                       subtitle=subtitle_boolean)
        self.media_manager_worker.moveToThread(self.media_manager_thread)
        self.media_manager_thread.started.connect(self.media_manager_worker.run)
        self.media_manager_worker.finished.connect(self.media_manager_thread.quit)
        self.media_manager_worker.finished.connect(self.media_manager_worker.deleteLater)
        self.media_manager_thread.finished.connect(self.media_manager_thread.deleteLater)
        self.media_manager_thread.start()
        self.media_manager_run_button.setEnabled(False)
        self.media_manager_thread.finished.connect(
            lambda: self.media_manager_run_button.setEnabled(True)
        )
        self.media_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media complete!\n")
        )
        self.media_manager_thread.finished.connect(
            lambda: self.media_manager_refresh_list()
        )

    def media_manager_media_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting media location to look for media in!\n")
        media_manager_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                        os.path.expanduser("~"),
                                                                        QFileDialog.ShowDirsOnly)
        if media_manager_directory_name == None or media_manager_directory_name == "":
            media_manager_directory_name = os.path.expanduser("~")
        self.media_manager_media_location_label.setText(media_manager_directory_name)
        self.media_manager.set_media_directory(media_manager_directory_name)
        self.media_manager.find_media()
        files = ""
        for file in self.media_manager.get_media_list():
            files = f"{files}\n{file}"
        self.media_manager_files_label.setText(files.strip())

    def media_manager_refresh_list(self):
        self.media_manager.set_media_directory(self.media_manager_move_location_label.text())
        self.media_manager.find_media()
        files = ""
        for file in self.media_manager.get_media_list():
            files = f"{files}\n{file}"
        self.media_manager_files_label.setText(files.strip())

    def media_manager_move_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting move location for media\n")
        media_manager_move_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                             os.path.expanduser("~"),
                                                                             QFileDialog.ShowDirsOnly)
        if media_manager_move_directory_name == None or media_manager_move_directory_name == "":
            media_manager_move_directory_name = os.path.expanduser("~")
        self.media_manager_move_location_label.setText(media_manager_move_directory_name)


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
