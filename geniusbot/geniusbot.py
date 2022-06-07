#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
from time import sleep
from videodownloader import VideoDownloader
from webarchiver import Webarchiver
# from report_merger import ReportMerge
# from analytic_profiler import ReportAnalyzer
from version import __version__, __author__, __credits__

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
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal


# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        for i in range(5):
            sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()


class VideoWorker(QThread):

    def __init__(self, video_downloader, videos, progress_bar, download_button):
        super().__init__()
        self.video_downloader = video_downloader
        self.videos = videos
        self.progress_bar = progress_bar
        self.download_button = download_button

    def run(self):
        for video_index in range(0, len(self.videos)):
            self.video_downloader.download_video(self.videos[video_index])
            self.progress_bar.setValue(int(((1 + video_index) / len(self.videos)) * 100))
        self.download_button.setEnabled(True)


class GeniusBot(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicksCount = 0
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
        self.channel_field_label = QLabel("YouTube Channel/User ►")
        self.channel_field_editor = QLineEdit()
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_videos)
        self.open_file_button = QPushButton("Open File")
        self.save_location_button = QPushButton("Save Location")
        self.video_progress_bar = QProgressBar()

        # Create and connect widgets
        self.clicksLabel = QLabel("Counting: 0 clicks")
        self.clicksLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.stepLabel = QLabel("Long-Running Step: 0")
        self.stepLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.countBtn = QPushButton("Click me!")
        self.countBtn.clicked.connect(self.countClicks)
        self.longRunningBtn = QPushButton("Long-Running Task!")
        self.longRunningBtn.clicked.connect(self.runLongTask)

        # Set the tab layout
        layout = QGridLayout()
        layout.addWidget(self.video_links_label, 0, 0, 1, 2)
        layout.addWidget(self.video_links_editor, 1, 0, 1, 2)
        layout.addWidget(self.channel_field_label, 2, 0, 1, 1)
        layout.addWidget(self.channel_field_editor, 2, 1, 1, 1)
        layout.addWidget(self.open_file_button, 3, 0, 1, 1)
        layout.addWidget(self.save_location_button, 3, 1, 1, 1)
        layout.addWidget(self.download_button, 4, 0, 1, 2)
        layout.addWidget(self.video_progress_bar, 5, 0, 1, 2)
        # layout.addWidget(self.clicksLabel)
        # layout.addWidget(self.countBtn)
        # layout.addWidget(self.stepLabel)
        # layout.addWidget(self.longRunningBtn)
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


    def countClicks(self):
        self.clicksCount += 1
        self.clicksLabel.setText(f"Counting: {self.clicksCount} clicks")

    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")

    def update_progress_bar(self, video_index, total_videos):
        self.video_progress_bar.setValue(int(((video_index + 1) / total_videos) * 100))

    def download_videos(self):
        videos = self.video_links_editor.toPlainText()
        videos = videos.rstrip()
        videos = videos.split('\n')

        self.worker = VideoWorker(self.video_downloader, videos, self.video_progress_bar, self.download_button)
        self.worker.start()
        self.download_button.setEnabled(False)


    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.longRunningBtn.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.longRunningBtn.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )


def geniusbot(argv):
    app = QApplication(sys.argv)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot(sys.argv[1:])


if __name__ == "__main__":
    geniusbot(sys.argv[1:])


