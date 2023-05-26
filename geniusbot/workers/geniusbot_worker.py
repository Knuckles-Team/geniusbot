#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QObject, pyqtSignal


class GeniusBotWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, geniusbot_chatbot, geniusbot_chat, text):
        super().__init__()
        self.geniusbot_chatbot = geniusbot_chatbot
        self.geniusbot_chat = geniusbot_chat
        self.text = text
        self.default_text = "Hello, my name is Geniusbot and I'm an artificially intelligent robot that can help you with"

    def run(self):
        """Long-running task."""
        old_text = self.geniusbot_chat.text()
        if self.geniusbot_chatbot.get_loaded() is False:
            self.geniusbot_chat.setText(f"{self.geniusbot_chat.text()}\n"
                                        f"[Genius Bot] Attempting to load intelligence...")
            self.geniusbot_chatbot.set_output_length(output_length=500)
            self.geniusbot_chatbot.scale_intelligence()
            self.geniusbot_chatbot.load_model()
            self.geniusbot_chat.setText(f"{self.geniusbot_chat.text()}\n"
                                        f"[Genius Bot] Loaded {self.geniusbot_chatbot.get_intelligence_level()} "
                                        f"intelligence level!")
        if self.text == '':
            self.text = self.default_text
        self.geniusbot_chat.setText(f"{old_text}\n[Genius Bot] Processing ...")
        response = self.geniusbot_chatbot.chat(prompt=self.text)
        self.geniusbot_chat.setText(f"{old_text}\n[Genius Bot] {response}")
        self.progress.emit(100)
        self.finished.emit()
