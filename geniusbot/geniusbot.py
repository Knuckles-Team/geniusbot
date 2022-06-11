#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from io import StringIO
from PyQt5.QtGui import QIcon, QFont
from webarchiver import Webarchiver
try:
    from geniusbot.videodownloader import VideoDownloader
except Exception as e:
    from videodownloader import VideoDownloader
try:
    from geniusbot.version import __version__, __author__, __credits__
except Exception as e:
    from version import __version__, __author__, __credits__
# from report_merger import ReportMerge
# from analytic_profiler import ReportAnalyzer

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
    QFileDialog, QScrollArea, QComboBox, QSpinBox,
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class WebarchiverWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, webarchiver, websites, console, zoom=100, dpi=1, filetype="png"):
        super().__init__()
        self.webarchiver = webarchiver
        self.websites = websites
        self.console = console
        self.zoom = zoom
        self.dpi = dpi
        self.filetype = filetype


    def run(self):
        """Long-running task."""
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        self.webarchiver.launch_browser()
        self.webarchiver.set_dpi_level(self.dpi)
        sys.stdout = old_stdout
        result_string = result.getvalue()
        self.console.setText(f"{self.console.text()}\n{result_string}")

        for website_index in range(0, len(self.websites)):
            self.webarchiver.append_link(self.websites[website_index])
            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            self.webarchiver.fullpage_screenshot(url=self.websites[website_index], zoom_percentage=self.zoom, filetype=self.filetype)
            sys.stdout = old_stdout
            result_string = result.getvalue()
            self.console.setText(f"{self.console.text()}\n{result_string}")
            self.progress.emit(int(((1 + website_index) / len(self.websites)) * 100))
            self.webarchiver.reset_links()

        self.webarchiver.quit_driver()

        self.finished.emit()


class VideoWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, video_downloader, videos, console):
        super().__init__()
        self.video_downloader = video_downloader
        self.videos = videos
        self.console = console

    def run(self):
        """Long-running task."""
        for video_index in range(0, len(self.videos)):
            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            self.video_downloader.download_video(self.videos[video_index])
            sys.stdout = old_stdout
            result_string = result.getvalue()
            self.console.setText(f"{self.console.text()}\n{result_string}")
            self.progress.emit(int(((1 + video_index) / len(self.videos)) * 100))
        self.finished.emit()


# class for scrollable label
class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setStyleSheet("background-color: #211f1f;")

        self.scroll_bar = self.verticalScrollBar()
        self.scroll_bar.rangeChanged.connect(lambda: self.scroll_bar.setValue(self.scroll_bar.maximum()))
        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)
        self.label.setFont(QFont('Monospace', 10))
        self.label.setStyleSheet("background-color: #211f1f; color: white;")

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

        self.setHidden(True)


    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    # the text() method
    def text(self):
        return self.label.text()

    def hide(self):
        if self.isHidden():
            self.setHidden(False)
        else:
            self.setHidden(True)


class GeniusBot(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_downloader = VideoDownloader()
        self.webarchiver = Webarchiver()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Genius Bot")
        self.setWindowIcon(QIcon(f'{os.path.dirname(os.path.realpath(__file__))}/img/geniusbot.ico'))
        self.setStyleSheet("background-color: #bfc3c9;")
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
        self.tabwidget.setStyleSheet("background-color: #f5f5f5;")
        self.tabwidget.addTab(self.tab1, "Tab 1")
        self.tabwidget.addTab(self.tab2, "Tab 2")
        self.tabwidget.addTab(self.tab3, "Tab 3")
        # self.tabwidget.addTab(self.tab4, "Tab 4")
        # self.tabwidget.addTab(self.tab5, "Tab 5")
        # self.tabwidget.addTab(self.tab6, "Tab 6")
        self.tab1_home()
        self.tab2_video_downloader()
        self.tab3_webarchiver()
        # self.tab4UI()
        # self.tab5UI()
        # self.tab6UI()

        # Set the main gui layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.buttonsWidget = QWidget()
        self.buttonsWidgetLayout = QHBoxLayout(self.buttonsWidget)
        self.console_label = QLabel("Console")
        self.hide_console_button = QPushButton("+")
        self.hide_console_button.clicked.connect(self.hide_console)
        self.buttonsWidgetLayout.addWidget(self.console_label)
        self.buttonsWidgetLayout.addWidget(self.hide_console_button)
        self.buttonsWidgetLayout.setStretch(0, 24)
        self.buttonsWidgetLayout.setStretch(1, 1)
        self.buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.console = ScrollLabel(self)
        self.console.setText(f"""Genius Bot Console:\n""")
        layout.addWidget(self.buttonsWidget)
        layout.addWidget(self.console)
        layout.setStretch(0, 24)
        layout.setStretch(1, 1)
        layout.setStretch(2, 3)
        self.centralWidget.setLayout(layout)

    def tab1_home(self):
        # self.console = QLabel(
        #     f"""GeniusBot at your service! What can we help you with?\n
        #     1. Video Downloader\n
        #     2. Web Archiver\n
        #     3. Analytical Profiler\n
        #     4. Report Merger\n
        #     5. Subtitle Shifter\n
        # """)
        self.homelabel = QLabel(self)
        self.homelabel.setText(
            f"""GeniusBot at your service! What can we help you with?\n
            1. Video Downloader\n
            2. Web Archiver\n            
            3. Analytical Profiler\n
            4. Report Merger\n
            5. Subtitle Shifter\n
        """)
        layout = QVBoxLayout()
        layout.addWidget(self.homelabel)
        self.tabwidget.setTabText(0, "Home")
        self.tab1.setLayout(layout)

    def tab2_video_downloader(self):
        # Video Download Widgets
        self.video_links_label = QLabel("Video Link(s) ▼")
        self.video_links_editor = QPlainTextEdit()
        self.channel_field_label = QPushButton("Channel/User")
        self.channel_field_label.clicked.connect(self.add_channel_videos)
        self.channel_field_editor = QLineEdit()
        self.video_download_button = QPushButton("Download")
        self.video_download_button.clicked.connect(self.download_videos)
        self.open_video_file_button = QPushButton("Open File")
        self.open_video_file_button.clicked.connect(self.open_video_file)
        self.video_open_file_label = QLabel("None")
        self.video_save_location_button = QPushButton("Save Location")
        self.video_save_location_button.clicked.connect(self.save_location)
        self.video_save_location_label = QLabel(f'{os.path.expanduser("~")}/Downloads')
        self.video_progress_bar = QProgressBar()

        # Set the tab layout
        video_layout = QGridLayout()
        video_layout.addWidget(self.video_links_label, 0, 0, 1, 2)
        video_layout.addWidget(self.video_links_editor, 1, 0, 1, 2)
        video_layout.addWidget(self.channel_field_label, 2, 0, 1, 1)
        video_layout.addWidget(self.channel_field_editor, 2, 1, 1, 1)
        video_layout.addWidget(self.open_video_file_button, 3, 0, 1, 1)
        video_layout.addWidget(self.video_open_file_label, 3, 1, 1, 2)
        video_layout.addWidget(self.video_save_location_button, 4, 0, 1, 1)
        video_layout.addWidget(self.video_save_location_label, 4, 1, 1, 2)
        video_layout.addWidget(self.video_download_button, 5, 0, 1, 2)
        video_layout.addWidget(self.video_progress_bar, 6, 0, 1, 2)
        self.tabwidget.setTabText(1, "Video Downloader")
        self.tab2.setLayout(video_layout)

    def tab3_webarchiver(self):
        # Video Download Widgets
        self.web_links_label = QLabel("Web Link(s) ▼")
        self.web_links_editor = QPlainTextEdit()
        self.archive_button = QPushButton("Screenshot")
        self.archive_button.clicked.connect(self.screenshot_websites)
        self.open_webfile_button = QPushButton("Open File")
        self.open_webfile_button.clicked.connect(self.open_webfile)
        self.open_webfile_label = QLabel("None")
        self.save_web_location_button = QPushButton("Save Location")
        self.save_web_location_button.clicked.connect(self.save_web_location)
        self.save_web_location_label = QLabel(f'{os.path.expanduser("~")}/Downloads')
        self.web_dpi_label = QLabel("DPI")
        self.web_dpi_spin_box = QSpinBox(self)
        self.web_dpi_spin_box.setRange(0, 2)
        self.web_dpi_spin_box.setValue(1)
        self.web_file_type_label = QLabel("Filetype")
        self.web_links_file_type = QComboBox()
        self.web_links_file_type.addItems(['PNG', 'JPEG'])
        self.web_zoom_label = QLabel("Zoom")
        self.web_zoom_spin_box = QSpinBox(self)
        self.web_zoom_spin_box.setRange(50, 200)
        self.web_zoom_spin_box.setValue(100)
        self.web_progress_bar = QProgressBar()

        # Set the tab layout
        webarchiver_layout = QGridLayout()
        webarchiver_layout.addWidget(self.web_links_label, 0, 0, 1, 6)
        webarchiver_layout.addWidget(self.web_links_editor, 1, 0, 1, 6)
        webarchiver_layout.addWidget(self.web_file_type_label, 2, 0, 1, 1, alignment=Qt.AlignRight)
        webarchiver_layout.addWidget(self.web_links_file_type, 2, 1, 1, 1)
        webarchiver_layout.addWidget(self.web_dpi_label, 2, 2, 1, 1, alignment=Qt.AlignRight)
        webarchiver_layout.addWidget(self.web_dpi_spin_box, 2, 3, 1, 1)
        webarchiver_layout.addWidget(self.web_zoom_label, 2, 4, 1, 1, alignment=Qt.AlignRight)
        webarchiver_layout.addWidget(self.web_zoom_spin_box, 2, 5, 1, 1)
        webarchiver_layout.addWidget(self.open_webfile_button, 3, 0, 1, 1)
        webarchiver_layout.addWidget(self.open_webfile_label, 3, 1, 1, 4)
        webarchiver_layout.addWidget(self.save_web_location_button, 4, 0, 1, 1)
        webarchiver_layout.addWidget(self.save_web_location_label, 4, 1, 1, 4)
        webarchiver_layout.addWidget(self.archive_button, 5, 0, 1, 6)
        webarchiver_layout.addWidget(self.web_progress_bar, 6, 0, 1, 6)
        self.tabwidget.setTabText(2, "Web Archiver")
        self.tab3.setLayout(webarchiver_layout)

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

    def hide_console(self):
        if self.hide_console_button.text() == "+":
            self.hide_console_button.setText("-")
        else:
            self.hide_console_button.setText("+")
        self.console.hide()

    def report_web_progress_bar(self, n):
        self.web_progress_bar.setValue(n)

    def screenshot_websites(self):
        self.web_progress_bar.setValue(0)
        websites = self.web_links_editor.toPlainText()
        websites = websites.strip()
        websites = websites.split('\n')
        if websites[0] != '':
            self.webarchiver_thread = QThread()
            self.webarchiver_worker = WebarchiverWorker(self.webarchiver, websites, self.console, self.web_zoom_spin_box.value(), dpi=self.web_dpi_spin_box.value(), filetype=self.web_links_file_type.currentText())
            self.webarchiver_worker.moveToThread(self.webarchiver_thread)
            self.webarchiver_thread.started.connect(self.webarchiver_worker.run)
            self.webarchiver_worker.finished.connect(self.webarchiver_thread.quit)
            self.webarchiver_worker.finished.connect(self.webarchiver_worker.deleteLater)
            self.webarchiver_thread.finished.connect(self.webarchiver_thread.deleteLater)
            self.webarchiver_worker.progress.connect(self.report_web_progress_bar)
            self.webarchiver_thread.start()
            self.archive_button.setEnabled(False)
            self.webarchiver_thread.finished.connect(
                lambda: self.archive_button.setEnabled(True)
            )


    def open_webfile(self):
        print("Opening Website URL file")
        website_file_name = QFileDialog.getOpenFileName(self, 'File with URL(s)')
        print(website_file_name[0])
        self.open_webfile_button.setText(website_file_name[0])

        with open(website_file_name[0], 'r') as file:
            websites = file.read()
        websites = websites + self.web_links_editor.toPlainText()
        websites = websites.strip()
        self.web_links_editor.setPlainText(websites)

    def save_web_location(self):
        print("Setting save location for screenshots")
        web_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.save_web_location_label.setText(web_directory_name)
        self.webarchiver.set_save_path(web_directory_name)

    def report_video_progress_bar(self, n):
        self.video_progress_bar.setValue(n)

    def download_videos(self):
        self.video_progress_bar.setValue(0)
        videos = self.video_links_editor.toPlainText()
        videos = videos.strip()
        videos = videos.split('\n')

        if videos[0] != '':
            self.video_thread = QThread()
            self.video_worker = VideoWorker(self.video_downloader, videos, self.console)
            self.video_worker.moveToThread(self.video_thread)
            self.video_thread.started.connect(self.video_worker.run)
            self.video_worker.finished.connect(self.video_thread.quit)
            self.video_worker.finished.connect(self.video_worker.deleteLater)
            self.video_thread.finished.connect(self.video_thread.deleteLater)
            self.video_worker.progress.connect(self.report_video_progress_bar)
            self.video_thread.start()
            self.video_download_button.setEnabled(False)
            self.video_thread.finished.connect(
                lambda: self.video_download_button.setEnabled(True)
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

    def open_video_file(self):
        print("Opening Video URL file")
        video_file_name = QFileDialog.getOpenFileName(self, 'File with Video URL(s)')
        print(video_file_name[0])
        self.video_open_file_label.setText(video_file_name[0])

        with open(video_file_name[0], 'r') as file:
            videos = file.read()
        videos = videos + self.video_links_editor.toPlainText()
        videos = videos.strip()
        self.video_links_editor.setPlainText(videos)

    def save_location(self):
        print("Setting save location for videos")
        video_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.video_save_location_label.setText(video_directory_name)
        self.video_downloader.set_save_path(video_directory_name)

def geniusbot(argv):
    app = QApplication(sys.argv)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot(sys.argv[1:])


if __name__ == "__main__":
    geniusbot(sys.argv[1:])


