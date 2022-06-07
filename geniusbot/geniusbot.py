#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from time import sleep
from geniusbot.videodownloader import VideoDownloader
from webarchiver import Webarchiver
# from report_merger import ReportMerge
# from analytic_profiler import ReportAnalyzer
from geniusbot.version import __version__, __author__, __credits__

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QGridLayout, QFormLayout, QHBoxLayout, QRadioButton, QLineEdit, QCheckBox, QPlainTextEdit, QProgressBar,
    QFileDialog,
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class VideoWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, video_downloader, videos):
        super().__init__()
        self.video_downloader = video_downloader
        self.videos = videos

    def run(self):
        """Long-running task."""
        for video_index in range(0, len(self.videos)):
            self.video_downloader.download_video(self.videos[video_index])
            self.progress.emit(int(((1 + video_index) / len(self.videos)) * 100))
        self.finished.emit()


class GeniusBot(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_downloader = VideoDownloader()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("GeniusBot")
        self.resize(690, 960)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tabwidget = QTabWidget()
        self.tabwidget.addTab(self.tab1, "Tab 1")
        self.tabwidget.addTab(self.tab2, "Tab 2")
        self.tabwidget.addTab(self.tab3, "Tab 3")
        self.tabwidget.addTab(self.tab4, "Tab 4")
        self.tabwidget.addTab(self.tab5, "Tab 5")
        self.tabwidget.addTab(self.tab6, "Tab 6")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.tab5UI()
        self.tab6UI()

        # Set the main gui layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.centralWidget.setLayout(layout)

    def tab1UI(self):
        self.homelabel = QLabel(f"""GeniusBot is a world class tool that allows you to do a lot of useful\n
                    things from a compact and portable application\n
                    1. YouTube Archive\n
                    2. Web Archive\n            
                    3. Analytical Profiler (Coming Soon)\n
                    4. Report Merger (Coming Soon)\n
                    5. FFMPEG Video/Audio Converter (Coming Soon)\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
                    """)
        layout = QVBoxLayout()
        layout.addWidget(self.homelabel)
        self.tabwidget.setTabText(0, "Home")
        self.tab1.setLayout(layout)

    def tab2UI(self):
        # Video Download Widgets
        self.video_links_label = QLabel("Video Link(s) ▼")
        self.video_links_editor = QPlainTextEdit()
        self.channel_field_label = QPushButton("Channel/User")
        self.channel_field_label.clicked.connect(self.add_channel_videos)
        self.channel_field_editor = QLineEdit()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_videos)
        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file)
        self.open_file_label = QLabel("None")
        self.save_location_button = QPushButton("Save Location")
        self.save_location_button.clicked.connect(self.save_location)
        self.save_location_label = QLabel(f'{os.path.expanduser("~")}/Downloads')
        self.video_progress_bar = QProgressBar()

        # Set the tab layout
        layout = QGridLayout()
        layout.addWidget(self.video_links_label, 0, 0, 1, 2)
        layout.addWidget(self.video_links_editor, 1, 0, 1, 2)
        layout.addWidget(self.channel_field_label, 2, 0, 1, 1)
        layout.addWidget(self.channel_field_editor, 2, 1, 1, 1)
        layout.addWidget(self.open_file_button, 3, 0, 1, 1)
        layout.addWidget(self.open_file_label, 3, 1, 1, 2)
        layout.addWidget(self.save_location_button, 4, 0, 1, 1)
        layout.addWidget(self.save_location_label, 4, 1, 1, 2)
        layout.addWidget(self.download_button, 5, 0, 1, 2)
        layout.addWidget(self.video_progress_bar, 6, 0, 1, 2)
        self.tabwidget.setTabText(1, "Video Downloader")
        self.tab2.setLayout(layout)

    def tab3UI(self):
        layout = QFormLayout()
        sex = QHBoxLayout()
        sex.addWidget(QRadioButton("Male"))
        sex.addWidget(QRadioButton("Female"))
        layout.addRow(QLabel("Sex"), sex)
        layout.addRow("Date of Birth", QLineEdit())
        self.tabwidget.setTabText(2, "Webarchiver")
        self.tab3.setLayout(layout)

    def tab4UI(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("subjects"))
        layout.addWidget(QCheckBox("Physics"))
        layout.addWidget(QCheckBox("Maths"))
        self.tabwidget.setTabText(3, "Report Manager")
        self.tab4.setLayout(layout)

    def tab5UI(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("subjects"))
        layout.addWidget(QCheckBox("Physics"))
        layout.addWidget(QCheckBox("Maths"))
        self.tabwidget.setTabText(4, "Analytic Profiler")
        self.tab5.setLayout(layout)

    def tab6UI(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("subjects"))
        layout.addWidget(QCheckBox("Physics"))
        layout.addWidget(QCheckBox("Maths"))
        self.tabwidget.setTabText(5, "Subshift")
        self.tab6.setLayout(layout)

    def report_video_progress_bar(self, n):
        self.video_progress_bar.setValue(n)

    def download_videos(self):
        self.video_progress_bar.setValue(0)
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')

        if videos[0] != '':
            self.thread = QThread()
            self.worker = VideoWorker(self.video_downloader, videos)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.report_video_progress_bar)
            self.thread.start()
            self.download_button.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.download_button.setEnabled(True)
            )

    def add_channel_videos(self):
        print("Adding Channel videos")
        self.video_downloader.get_channel_videos(self.channel_field_editor.text())
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')
        videos = videos + self.video_downloader.get_links()
        videos = '\n'.join(videos)
        self.video_links_editor.setPlainText(videos)

    def open_file(self):
        print("Opening Video URL file")
        video_file_name = QFileDialog.getOpenFileName(self, 'File with Video URL(s)')
        print(video_file_name[0])
        self.open_file_label.setText(video_file_name[0])

        with open(video_file_name[0], 'r') as file:
            videos = file.read()
        videos = videos + self.video_links_editor.toPlainText()
        videos = videos.strip()
        self.video_links_editor.setPlainText(videos)

    def save_location(self):
        print("Setting save location for videos")
        directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.save_location_label.setText(directory_name)
        self.video_downloader.set_save_path(directory_name)

def geniusbot(argv):
    app = QApplication(sys.argv)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot(sys.argv[1:])


if __name__ == "__main__":
    geniusbot(sys.argv[1:])


