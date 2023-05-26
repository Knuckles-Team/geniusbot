#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from io import StringIO


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
            self.webarchiver.full_page_screenshot(url=self.websites[website_index], zoom_percentage=self.zoom,
                                                  filetype=self.filetype)
            self.progress.emit(int(((1 + website_index) / len(self.websites)) * 100))
            self.webarchiver.reset_links()

        self.webarchiver.quit_driver()

        self.finished.emit()
