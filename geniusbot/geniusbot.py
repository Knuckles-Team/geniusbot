#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subshift
from io import StringIO
from PyQt5.QtGui import QIcon, QFont, QTextCursor
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

yellow = "#FFA500"
green = "#2E8B57"
orange = "#FF7518"
blue = "#4682B4"
red = ""
purple = ""

class OutputWrapper(QObject):
    outputWritten = pyqtSignal(object, object)

    def __init__(self, parent, stdout=True):
        super().__init__(parent)
        if stdout:
            self._stream = sys.stdout
            sys.stdout = self
        else:
            self._stream = sys.stderr
            sys.stderr = self
        self._stdout = stdout

    def write(self, text):
        self._stream.write(text)
        self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            if self._stdout:
                sys.stdout = self._stream
            else:
                sys.stderr = self._stream
        except AttributeError:
            pass


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

class WebarchiverWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, webarchiver, websites, zoom=100, dpi=1, filetype="png"):
        super().__init__()
        self.webarchiver = webarchiver
        self.websites = websites
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

        for website_index in range(0, len(self.websites)):
            self.webarchiver.append_link(self.websites[website_index])
            self.webarchiver.fullpage_screenshot(url=self.websites[website_index], zoom_percentage=self.zoom, filetype=self.filetype)
            self.progress.emit(int(((1 + website_index) / len(self.websites)) * 100))
            self.webarchiver.reset_links()

        self.webarchiver.quit_driver()

        self.finished.emit()


class VideoWorker(QObject):
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
            self.video_downloader.download_video(self.videos[video_index], audio=self.audio)
            self.progress.emit(int(((1 + video_index) / len(self.videos)) * 100))
        self.finished.emit()


# class for scrollable label
class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setStyleSheet("background-color: #211f1f;")

        self.scroll_bar = self.verticalScrollBar()
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

    def setFont(self, font="Monospace"):
        self.label.setFont(QFont(font, 10))

    def setFontColor(self, background_color="#211f1f", color="white"):
        self.label.setStyleSheet(f"background-color: {background_color}; color: {color};")
        self.setStyleSheet(f"background-color: {background_color};")

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

    def setScrollWheel(self, location="Top"):
        if location == "Bottom":
            self.scroll_bar.rangeChanged.connect(lambda: self.scroll_bar.setValue(self.scroll_bar.maximum()))
        else:
            self.scroll_bar.rangeChanged.connect(lambda: self.scroll_bar.setValue(0))

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
        self.setWindowTitle(f"Genius Bot")
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
        self.tabwidget.addTab(self.tab4, "Tab 4")
        # self.tabwidget.addTab(self.tab5, "Tab 5")
        # self.tabwidget.addTab(self.tab6, "Tab 6")
        self.tab1_home()
        self.tab2_video_downloader()
        self.tab3_webarchiver()
        self.tab4_subshift()
        # self.tab5UI()
        # self.tab6UI()

        # Set the main gui layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)
        self.buttonsWidget = QWidget()
        self.buttonsWidgetLayout = QHBoxLayout(self.buttonsWidget)
        #self.console_label = QLabel("Console")
        self.hide_console_button = QPushButton("Console ◳")
        self.hide_console_button.setStyleSheet("background-color: #211f1f; color: white; font: bold;")
        self.hide_console_button.clicked.connect(self.hide_console)
        #self.buttonsWidgetLayout.addWidget(self.console_label)
        self.buttonsWidgetLayout.addWidget(self.hide_console_button)
        self.buttonsWidgetLayout.setStretch(0, 24)
        self.buttonsWidgetLayout.setStretch(1, 1)
        self.buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.console = ScrollLabel(self)
        self.console.setScrollWheel(location="Bottom")
        self.console.setText(f"[Genius Bot] Version: {__version__}\n[Genius Bot] Console Output of Running Tasks\n")
        stdout = OutputWrapper(self, True)
        stdout.outputWritten.connect(self.console_output)
        stderr = OutputWrapper(self, False)
        stderr.outputWritten.connect(self.console_output)
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
            f"""Genius Bot at your service! What can we help you with?\n
            1. Video Downloader\n
            2. Web Archiver\n
            3. Subtitle Shifter\n                        
            4. Analytical Profiler\n
            5. Report Merger\n
        """)
        layout = QVBoxLayout()
        layout.addWidget(self.homelabel)
        self.tabwidget.setTabText(0, "Home")
        self.tab1.setLayout(layout)

    def tab2_video_downloader(self):
        # Video Download Widgets
        self.video_links_label = QLabel("Paste Video Link(s) Below ↴")
        self.video_links_label.setStyleSheet(f"color: black; font-size: 11pt;")
        self.video_links_editor = QPlainTextEdit()
        self.channel_field_label = QPushButton("Channel/User")
        self.channel_field_label.setStyleSheet(f"background-color: {yellow}; color: white; font: bold;")
        self.channel_field_label.clicked.connect(self.add_channel_videos)
        self.channel_field_editor = QLineEdit()
        self.video_download_button = QPushButton("Download ￬")
        self.video_download_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.video_download_button.clicked.connect(self.download_videos)
        self.open_video_file_button = QPushButton("Open File")
        self.open_video_file_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.open_video_file_button.clicked.connect(self.open_video_file)
        self.video_open_file_label = QLabel("None")
        self.video_save_location_button = QPushButton("Save Location")
        self.video_save_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
        self.video_save_location_button.clicked.connect(self.save_location)
        self.video_save_location_label = QLabel(f'{os.path.expanduser("~")}/Downloads')
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
        self.tabwidget.setTabText(1, "Video Downloader")
        self.tab2.setLayout(video_layout)

    def tab3_webarchiver(self):
        # Video Download Widgets
        self.web_links_label = QLabel("Paste Website Link(s) Below ↴")
        self.web_links_label.setStyleSheet(f"color: black; font-size: 11pt;")
        self.web_links_editor = QPlainTextEdit()
        self.archive_button = QPushButton("Archive ￬")
        self.archive_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.archive_button.clicked.connect(self.screenshot_websites)
        self.open_webfile_button = QPushButton("Open File")
        self.open_webfile_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.open_webfile_button.clicked.connect(self.open_webfile)
        self.open_webfile_label = QLabel("None")
        self.save_web_location_button = QPushButton("Save Location")
        self.save_web_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
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
        webarchiver_layout.setContentsMargins(3, 3, 3, 3)
        self.tabwidget.setTabText(2, "Website Archive")
        self.tab3.setLayout(webarchiver_layout)

    def tab4_subshift(self):
        self.open_subtitlefile_button = QPushButton("Open File")
        self.open_subtitlefile_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
        self.open_subtitlefile_button.clicked.connect(self.open_subtitlefile)
        self.shift_subtitle_button = QPushButton("Shift Subtitles ↹")
        self.shift_subtitle_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.shift_subtitle_button.clicked.connect(self.shift_subtitle)

        #self.subtitle_label = QLabel(self)
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
        self.tabwidget.setTabText(3, "Shift Subtitles")
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
        self.tabwidget.setTabText(5, "Report Manager")
        self.tab6.setLayout(layout)

    def console_output(self, text, stdout):
        #color = self.console.textColor()
        #self.console.moveCursor(QTextCursor.End)
        #self.console.setTextColor(color if stdout else self._err_color)
        self.console.setText(f"{self.console.text()}{text}")
        #self.console.setTextColor(color)

    def hide_console(self):
        if self.hide_console_button.text() == "Console ◳":
            self.hide_console_button.setText("Console _")
        else:
            self.hide_console_button.setText("Console ◳")
        self.console.hide()

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

    def report_web_progress_bar(self, n):
        self.web_progress_bar.setValue(n)

    def screenshot_websites(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Taking screenshots...\n")
        self.web_progress_bar.setValue(1)
        websites = self.web_links_editor.toPlainText()
        websites = websites.strip()
        websites = websites.split('\n')
        if websites[0] != '':
            self.webarchiver_thread = QThread()
            self.webarchiver_worker = WebarchiverWorker(self.webarchiver, websites, self.web_zoom_spin_box.value(), dpi=self.web_dpi_spin_box.value(), filetype=self.web_links_file_type.currentText())
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
            self.console.setText(f"[Genius Bot] Screenshots captured!\n")

    def open_webfile(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Opening Website URL file\n")
        website_file_name = QFileDialog.getOpenFileName(self, 'File with URL(s)')
        print(website_file_name[0])
        self.open_webfile_label.setText(website_file_name[0])

        with open(website_file_name[0], 'r') as file:
            websites = file.read()
        websites = websites + self.web_links_editor.toPlainText()
        websites = websites.strip()
        self.web_links_editor.setPlainText(websites)

    def save_web_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for screenshots\n")
        web_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.save_web_location_label.setText(web_directory_name)
        self.webarchiver.set_save_path(web_directory_name)

    def report_video_progress_bar(self, n):
        self.video_progress_bar.setValue(n)

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
            self.video_worker = VideoWorker(self.video_downloader, videos, audio_boolean)
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
            self.console.setText(f"[Genius Bot] Videos downloaded!\n")

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

    def save_location(self):
        self.console.setText(f"{self.console.text()}\n[Genius Bot] Setting save location for videos\n")
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


