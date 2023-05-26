#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from io import StringIO
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGridLayout, QPlainTextEdit, QProgressBar,
    QFileDialog, QComboBox, QSpinBox
)
from PyQt5.QtCore import QThread
try:
    from geniusbot.colors import yellow, green, orange, blue, red, purple
except Exception as e:
    from colors import yellow, green, orange, blue, red, purple


def webarchiver_tab(self):
    # Video Download Widgets
    self.web_links_label = QLabel("Paste Website URL(s) Below ↴")
    self.web_links_label.setStyleSheet(f"color: black; font-size: 11pt;")
    self.web_links_editor = QPlainTextEdit()
    self.archive_button = QPushButton("Archive ￬")
    self.archive_button.setStyleSheet(f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
    self.archive_button.clicked.connect(screenshot_websites)
    self.open_webfile_button = QPushButton("Open File")
    self.open_webfile_button.setStyleSheet(f"background-color: {green}; color: white; font: bold;")
    self.open_webfile_button.clicked.connect(open_webfile)
    self.open_webfile_label = QLabel("None")
    self.save_web_location_button = QPushButton("Save Location")
    self.save_web_location_button.setStyleSheet(f"background-color: {orange}; color: white; font: bold;")
    self.save_web_location_button.clicked.connect(save_web_location)
    self.save_web_location_label = QLabel(f'{os.path.expanduser("~")}'.replace("\\", "/"))
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
    self.tab_widget.setTabText(3, "Website Archive")
    self.tab4.setLayout(webarchiver_layout)


def screenshot_websites(self):
    self.console.setText(f"{self.console.text()}\n[Genius Bot] Taking screenshots...\n")
    self.web_progress_bar.setValue(1)
    websites = self.web_links_editor.toPlainText()
    websites = websites.strip()
    websites = websites.split('\n')
    if websites[0] != '':
        self.webarchiver_thread = QThread()
        self.webarchiver_worker = WebarchiverWorker(self.webarchiver, websites, self.web_zoom_spin_box.value(),
                                                    dpi=self.web_dpi_spin_box.value(),
                                                    filetype=self.web_links_file_type.currentText())
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
        self.webarchiver_thread.finished.connect(
            lambda: self.console.setText(f"{self.console.text()}\n[Genius Bot] Screenshots captured!\n")
        )


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
    web_directory_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', os.path.expanduser("~"),
                                                          QFileDialog.ShowDirsOnly)
    if web_directory_name == None or web_directory_name == "":
        web_directory_name = os.path.expanduser("~")
    self.save_web_location_label.setText(web_directory_name)
    self.webarchiver.set_save_path(web_directory_name)


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
        self.browser = "Chrome"
        self.executor = "Local"
        self.processes = 1

    def run(self):
        """Long-running task."""
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        sys.stdout = old_stdout
        result_string = result.getvalue()


        for website_index in range(0, len(self.websites)):
            self.webarchiver.append_link(self.websites[website_index])
            self.webarchiver.full_page_screenshot(url=self.websites[website_index], zoom_percentage=self.zoom,
                                                  filetype=self.filetype)
            self.progress.emit(int(((1 + website_index) / len(self.websites)) * 100))
            self.webarchiver.reset_links()

            self.webarchiver.set_zoom_level(self.zoom)
            self.webarchiver.set_image_format(self.filetype)
            self.webarchiver.set_browser(browser=self.browser)
            self.webarchiver.set_executor(executor=self.executor)
            self.webarchiver.set_processes(processes=self.processes)
            self.webarchiver.screenshot_urls_in_parallel(parallel_urls=self.webarchiver.urls)

        self.webarchiver.quit_driver()

        self.finished.emit()
