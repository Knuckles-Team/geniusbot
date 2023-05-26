#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal
import os


class MediaWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, media_manager, directory, move, destination, subtitle):
        super().__init__()
        self.media_manager = media_manager
        self.directory = directory
        self.move = move
        self.destination = destination
        self.subtitle = subtitle

    def run(self):
        """Long-running task."""
        self.media_manager.set_media_directory(media_directory=self.directory)
        self.media_manager.find_media()
        self.media_manager.clean_media(subtitle=self.subtitle)
        if os.path.isdir(os.path.normpath(self.destination)) and self.move is True:
            self.media_manager.move_media(target_directory=self.destination)

        self.progress.emit(100)
        self.finished.emit()
