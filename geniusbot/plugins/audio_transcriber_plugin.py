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

package = 'audio-transcriber'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from audio_transcriber import AudioTranscriber
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class AudioTranscriberTab(QWidget):
    def __init__(self, console):
        super(AudioTranscriberTab, self).__init__()

        # f"-b | --bitrate   [ Bitrate to use during recording ]\n"
        # f"-c | --channels  [ Number of channels to use during recording ]\n"
        # f"-d | --directory [ Directory to save recording ]\n"
        # f"-e | --export    [ Export txt, srt, & vtt ]\n"
        # f"-f | --file      [ File to transcribe ]\n"
        # f"-l | --language  [ Language to transcribe <'en', 'fa', 'es', 'zh'> ]\n"
        # f"-m | --model     [ Model to use: <tiny, base, small, medium, large> ]\n"
        # f"-n | --name      [ Name of recording ]\n"
        # f"-r | --record    [ Specify number of seconds to record to record from microphone ]\n"

        self.console = console
        self.audio_transcriber_manager = AudioTranscriber()
        self.audio_transcriber_tab = QWidget()
        audio_transcriber_manager_layout = QGridLayout()
        self.audio_transcriber_manager_media_location_button = QPushButton("File to Transcribe")
        self.audio_transcriber_manager_media_location_button.setStyleSheet(
            f"background-color: {orange}; color: white; font: bold;")
        self.audio_transcriber_manager_media_location_button.clicked.connect(
            self.audio_transcriber_manager_media_location)
        self.audio_transcriber_manager_media_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.audio_transcriber_manager_move_location_button = QPushButton("Directory to Save Recordings")
        self.audio_transcriber_manager_move_location_button.setStyleSheet(
            f"background-color: {green}; color: white; font: bold;")
        self.audio_transcriber_manager_move_location_button.clicked.connect(
            self.audio_transcriber_manager_move_location)
        self.audio_transcriber_manager_move_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.subtitle_ticker = QCheckBox("Apply Subtitles")
        self.move_ticker = QCheckBox("Move Media")
        self.audio_transcriber_manager_files_label = ScrollLabel(self)
        self.audio_transcriber_manager_files_label.hide()
        self.audio_transcriber_manager_files_label.setText(f"Media files found will be shown here\n")
        self.audio_transcriber_manager_files_label.setFont("Arial")
        self.audio_transcriber_manager_files_label.setFontColor(background_color="white", color="black")
        self.audio_transcriber_manager_files_label.setScrollWheel("Top")
        self.audio_transcriber_manager_run_button = QPushButton("Transcribe ⥀")
        self.audio_transcriber_manager_run_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.audio_transcriber_manager_run_button.clicked.connect(self.manage_media)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_media_location_button, 0, 0, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_media_location_label, 0, 1, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_move_location_button, 1, 0, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_move_location_label, 1, 1, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.move_ticker, 2, 0, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.subtitle_ticker, 2, 1, 1, 1)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_files_label, 3, 0, 1, 2)
        audio_transcriber_manager_layout.addWidget(self.audio_transcriber_manager_run_button, 4, 0, 1, 2)
        self.audio_transcriber_tab.setLayout(audio_transcriber_manager_layout)

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

        self.audio_transcriber_manager_thread = QThread()
        self.audio_transcriber_manager_worker = MediaManagerWorker(
            audio_transcriber_manager=self.audio_transcriber_manager,
            directory=self.audio_transcriber_manager_media_location_label.text(),
            move=move_boolean,
            destination=self.audio_transcriber_manager_move_location_label.text(),
            subtitle=subtitle_boolean)
        self.audio_transcriber_manager_worker.moveToThread(self.audio_transcriber_manager_thread)
        self.audio_transcriber_manager_thread.started.connect(self.audio_transcriber_manager_worker.run)
        self.audio_transcriber_manager_worker.finished.connect(self.audio_transcriber_manager_thread.quit)
        self.audio_transcriber_manager_worker.finished.connect(self.audio_transcriber_manager_worker.deleteLater)
        self.audio_transcriber_manager_thread.finished.connect(self.audio_transcriber_manager_thread.deleteLater)
        self.audio_transcriber_manager_thread.start()
        self.audio_transcriber_manager_run_button.setEnabled(False)
        self.audio_transcriber_manager_thread.finished.connect(
            lambda: self.audio_transcriber_manager_run_button.setEnabled(True)
        )
        self.audio_transcriber_manager_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Managing media complete!\n")
        )
        self.audio_transcriber_manager_thread.finished.connect(
            lambda: self.audio_transcriber_manager_refresh_list()
        )

    def audio_transcriber_manager_media_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting media location to look for media in!\n")
        audio_transcriber_manager_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                                    os.path.expanduser("~"),
                                                                                    QFileDialog.ShowDirsOnly)
        if audio_transcriber_manager_directory_name == None or audio_transcriber_manager_directory_name == "":
            audio_transcriber_manager_directory_name = os.path.expanduser("~")
        self.audio_transcriber_manager_media_location_label.setText(audio_transcriber_manager_directory_name)
        self.audio_transcriber_manager.set_media_directory(audio_transcriber_manager_directory_name)
        self.audio_transcriber_manager.find_media()
        files = ""
        for file in self.audio_transcriber_manager.get_media_list():
            files = f"{files}\n{file}"
        self.audio_transcriber_manager_files_label.setText(files.strip())

    def audio_transcriber_manager_refresh_list(self):
        self.audio_transcriber_manager.set_media_directory(self.audio_transcriber_manager_move_location_label.text())
        self.audio_transcriber_manager.find_media()
        files = ""
        for file in self.audio_transcriber_manager.get_media_list():
            files = f"{files}\n{file}"
        self.audio_transcriber_manager_files_label.setText(files.strip())

    def audio_transcriber_manager_move_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting move location for media\n")
        audio_transcriber_manager_move_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:',
                                                                                         os.path.expanduser("~"),
                                                                                         QFileDialog.ShowDirsOnly)
        if audio_transcriber_manager_move_directory_name == None or audio_transcriber_manager_move_directory_name == "":
            audio_transcriber_manager_move_directory_name = os.path.expanduser("~")
        self.audio_transcriber_manager_move_location_label.setText(audio_transcriber_manager_move_directory_name)


class MediaManagerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, audio_transcriber_manager, directory, move, destination, subtitle):
        super().__init__()
        self.audio_transcriber_manager = audio_transcriber_manager
        self.directory = directory
        self.move = move
        self.destination = destination
        self.subtitle = subtitle

    def run(self):
        """Long-running task."""
        self.audio_transcriber_manager.set_media_directory(media_directory=self.directory)
        self.audio_transcriber_manager.find_media()
        self.audio_transcriber_manager.clean_media(subtitle=self.subtitle)
        if os.path.isdir(os.path.normpath(self.destination)) and self.move is True:
            self.audio_transcriber_manager.move_media(target_directory=self.destination)

        self.progress.emit(100)
        self.finished.emit()
