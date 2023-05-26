#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


def media_downloader_tab(self):
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
    self.video_save_location_button.clicked.connect(self.save_location)
    self.video_save_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
    self.video_type_label = QLabel("Filetype")
    self.video_type_combobox = QComboBox()
    self.video_type_combobox.addItems(['Video', 'Audio'])
    self.video_type_combobox.setItemText(0, "Video")
    self.video_progress_bar = QProgressBar()

    # Set the tab layout
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
    self.tab_widget.setTabText(1, "Media Downloader")
    self.tab2.setLayout(video_layout)



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
