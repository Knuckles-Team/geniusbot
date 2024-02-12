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
package = 'rom-manager'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from rom_manager import RomManager
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class MediaManagerTab(QWidget):
    def __init__(self, console):
        super(MediaManagerTab, self).__init__()
        self.console = console
        self.rom_manager = RomManager()
        self.rom_manager_tab = QWidget()
        rom_manager_layout = QGridLayout()
        self.rom_manager_location_button = QPushButton("Media Location")
        self.rom_manager_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
        self.rom_manager_location_button.clicked.connect(self.rom_manager_location)
        self.rom_manager_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))

        self.subtitle_ticker = QCheckBox("Apply Subtitles")
        self.move_ticker = QCheckBox("Move Media")
        self.rom_manager_files_label = ScrollLabel(self)
        self.rom_manager_files_label.hide()
        self.rom_manager_files_label.setText(f"Media files found will be shown here\n")
        self.rom_manager_files_label.setFont("Arial")
        self.rom_manager_files_label.setFontColor(background_color="white", color="black")
        self.rom_manager_files_label.setScrollWheel("Top")
        self.rom_manager_run_button = QPushButton("Run ⥀")
        self.rom_manager_run_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.rom_manager_run_button.clicked.connect(self.manage_media)
        rom_manager_layout.addWidget(self.rom_manager_location_button, 0, 0, 1, 1)
        rom_manager_layout.addWidget(self.rom_manager_location_label, 0, 1, 1, 1)
        rom_manager_layout.addWidget(self.rom_manager_move_location_button, 1, 0, 1, 1)
        rom_manager_layout.addWidget(self.move_ticker, 2, 0, 1, 1)
        rom_manager_layout.addWidget(self.subtitle_ticker, 2, 1, 1, 1)
        rom_manager_layout.addWidget(self.rom_manager_files_label, 3, 0, 1, 2)
        rom_manager_layout.addWidget(self.rom_manager_run_button, 4, 0, 1, 2)
        self.rom_manager_tab.setLayout(rom_manager_layout)

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

        self.rom_manager_thread = QThread()
        self.rom_manager_worker = MediaManagerWorker(rom_manager=self.rom_manager,
                                                       directory=self.rom_manager_media_location_label.text(),
                                                       move=move_boolean,
                                                       destination=self.rom_manager_move_location_label.text(),
                                                       subtitle=subtitle_boolean)
        self.rom_manager_worker.moveToThread(self.rom_manager_thread)
        self.rom_manager_thread.started.connect(self.rom_manager_worker.run)
        self.rom_manager_worker.finished.connect(self.rom_manager_thread.quit)
        self.rom_manager_worker.finished.connect(self.rom_manager_worker.deleteLater)
        self.rom_manager_thread.finished.connect(self.rom_manager_thread.deleteLater)
        self.rom_manager_thread.start()
        self.rom_manager_run_button.setEnabled(False)
        self.rom_manager_thread.finished.connect(
            lambda: self.rom_manager_run_button.setEnabled(True)
        )
        self.rom_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media complete!\n")
        )
        self.rom_manager_thread.finished.connect(
            lambda: self.rom_manager_refresh_list()
        )

    def rom_manager_media_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting media location to look for media in!\n")
        rom_manager_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                        os.path.expanduser("~"),
                                                                        QFileDialog.ShowDirsOnly)
        if rom_manager_directory_name == None or rom_manager_directory_name == "":
            rom_manager_directory_name = os.path.expanduser("~")
        self.rom_manager_media_location_label.setText(rom_manager_directory_name)
        self.rom_manager.set_media_directory(rom_manager_directory_name)
        self.rom_manager.find_media()
        files = ""
        for file in self.rom_manager.get_media_list():
            files = f"{files}\n{file}"
        self.rom_manager_files_label.setText(files.strip())

    def rom_manager_refresh_list(self):
        self.rom_manager.set_media_directory(self.rom_manager_move_location_label.text())
        self.rom_manager.find_media()
        files = ""
        for file in self.rom_manager.get_media_list():
            files = f"{files}\n{file}"
        self.rom_manager_files_label.setText(files.strip())

    def rom_manager_move_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting move location for media\n")
        rom_manager_move_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                             os.path.expanduser("~"),
                                                                             QFileDialog.ShowDirsOnly)
        if rom_manager_move_directory_name == None or rom_manager_move_directory_name == "":
            rom_manager_move_directory_name = os.path.expanduser("~")
        self.rom_manager_move_location_label.setText(rom_manager_move_directory_name)


class RomManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, rom_manager, directory, move, destination, subtitle):
        super().__init__()
        self.rom_manager = rom_manager
        self.directory = directory
        self.move = move
        self.destination = destination
        self.subtitle = subtitle

    def run(self):
        """Long-running task."""
        self.rom_manager.set_media_directory(media_directory=self.directory)
        self.rom_manager.find_media()
        self.rom_manager.clean_media(subtitle=self.subtitle)
        if os.path.isdir(os.path.normpath(self.destination)) and self.move is True:
            self.rom_manager.move_media(target_directory=self.destination)

        self.progress.emit(100)
        self.finished.emit()
