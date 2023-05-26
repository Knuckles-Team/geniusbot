#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import subshift


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
