#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append("..")
from PyQt5.QtWidgets import (
    QGridLayout,
    QPushButton,
    QLabel,
    QPlainTextEdit,
    QLineEdit, QProgressBar, QComboBox, QWidget, QFileDialog
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
try:
    from qt.colors import yellow, green, orange, blue, red, purple
except ModuleNotFoundError:
    from geniusbot.qt.colors import yellow, green, orange, blue, red, purple
import pkg_resources
package = 'media-downloader'
try:
    dist = pkg_resources.get_distribution(package)
    print('{} ({}) is installed'.format(dist.key, dist.version))
    from media_downloader import MediaDownloader
except pkg_resources.DistributionNotFound:
    print('{} is NOT installed'.format(package))


class MediaDownloaderTab(QWidget):
    def __init__(self, console):
        super(MediaDownloaderTab, self).__init__()
        self.console = console
        self.video_downloader = MediaDownloader()
        self.media_downloader_tab = QWidget()
        # Video Download Widgets
        self.video_links_label = QLabel("Paste Video URL(s) Below ↴")
        self.video_links_label.setStyleSheet(f"color: black; font-size: 11pt;")
        self.video_links_editor = QPlainTextEdit()
        self.channel_field_label = QPushButton("Channel/User")
        self.channel_field_label.setStyleSheet(f"background-color: {yellow}; color: white; font: bold;")
        self.channel_field_label.clicked.connect(self.add_channel_videos)
        self.channel_field_editor = QLineEdit()
        self.video_download_button = QPushButton("Download ￬")
        self.video_download_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.video_download_button.clicked.connect(self.download_videos)
        self.open_video_file_button = QPushButton("Open File")
        self.open_video_file_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.open_video_file_button.clicked.connect(self.open_video_file)
        self.video_open_file_label = QLabel("None")
        self.video_save_location_button = QPushButton("Save Location")
        self.video_save_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
        self.video_save_location_button.clicked.connect(self.media_download_save_location)
        self.video_save_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
        self.video_type_label = QLabel("Filetype")
        self.video_type_combobox = QComboBox()
        self.video_type_combobox.addItems(['Video', 'Audio'])
        self.video_type_combobox.setItemText(0, "Video")
        self.video_progress_bar = QProgressBar()
        video_layout = QGridLayout()
        video_layout.addWidget(self.video_links_label, 0, 0, 1, 2)
        video_layout.addWidget(self.video_links_editor, 1, 0, 1, 2)
        video_layout.addWidget(self.video_type_label, 2, 0, 1, 1)
        video_layout.addWidget(self.video_type_combobox, 2, 1, 1, 2)
        video_layout.addWidget(self.channel_field_label, 3, 0, 1, 1)
        video_layout.addWidget(self.channel_field_editor, 3, 1, 1, 1)
        video_layout.addWidget(self.open_video_file_button, 4, 0, 1, 1)
        video_layout.addWidget(self.video_open_file_label, 4, 1, 1, 2)
        video_layout.addWidget(self.video_save_location_button, 5, 0, 1, 1)
        video_layout.addWidget(self.video_save_location_label, 5, 1, 1, 2)
        video_layout.addWidget(self.video_download_button, 6, 0, 1, 2)
        video_layout.addWidget(self.video_progress_bar, 7, 0, 1, 2)
        video_layout.setContentsMargins(3, 3, 3, 3)
        self.media_downloader_tab.setLayout(video_layout)

    def media_download_save_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for videos\n")
        video_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.expanduser("~"),
                                                                QFileDialog.ShowDirsOnly)
        if video_directory_name == None or video_directory_name == "":
            video_directory_name = os.path.expanduser("~")
        self.video_save_location_label.setText(video_directory_name)
        self.video_downloader.set_save_path(video_directory_name)

    def download_videos(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Downloading videos...\n")
        self.video_progress_bar.setValue(1)
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')

        if videos[0] != '':
            if self.video_type_combobox.currentText() == "Audio":
                audio_boolean = True
            else:
                audio_boolean = False
            self.video_thread = QThread()
            self.video_worker = MediaDownloaderWorker(self.video_downloader, videos, audio_boolean)
            self.video_worker.moveToThread(self.video_thread)
            self.video_thread.started.connect(self.video_worker.run)
            self.video_worker.finished.connect(self.video_thread.quit)
            self.video_worker.finished.connect(self.video_worker.deleteLater)
            self.video_thread.finished.connect(self.video_thread.deleteLater)
            self.video_worker.progress.connect(self.report_video_download_progress_bar)
            self.video_thread.start()
            self.video_download_button.setEnabled(False)
            self.video_thread.finished.connect(
                lambda: self.video_download_button.setEnabled(True)
            )
            self.video_thread.finished.connect(
                lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Videos downloaded!\n")
            )

    def add_channel_videos(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Adding Channel videos\n")
        self.video_downloader.get_channel_videos(self.channel_field_editor.text())
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')
        videos = videos + self.video_downloader.get_links()
        videos = '\n'.join(videos)
        self.video_links_editor.setPlainText(videos)

    def open_video_file(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening Video URL file\n")
        video_file_name = QFileDialog.getOpenFileName(self, 'File with Video URL(s)')
        print(video_file_name[0])
        self.video_open_file_label.setText(video_file_name[0])

        with open(video_file_name[0], 'r') as file:
            videos = file.read()
        videos = videos + self.video_links_editor.toPlainText()
        videos = videos.strip()
        self.video_links_editor.setPlainText(videos)

    def report_video_download_progress_bar(self, n):
        self.video_progress_bar.setValue(n)


class MediaDownloaderWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, video_downloader, videos, audio):
        super().__init__()
        self.video_downloader = video_downloader
        self.videos = videos
        self.audio = audio

    def run(self):
        """Long-running task."""
        for video_index in range(0, len(self.videos)):
            self.video_downloader.set_audio(audio=self.audio)
            self.video_downloader.download_video(self.videos[video_index])
            self.progress.emit(int(((1 + video_index) / len(self.videos)) * 100))
        self.finished.emit()
