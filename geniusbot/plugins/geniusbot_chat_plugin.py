#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append("..")
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QPlainTextEdit,
    QLineEdit, QProgressBar, QVBoxLayout, QTextEdit
)
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qt.colors import yellow, green, orange, blue, red, purple
from qt.scrollable_widget import ScrollLabel
from genius_chatbot import ChatBot


if os.name == "posix":
    import pwd
    user = pwd.getpwuid(os.geteuid()).pw_name
else:
    ukn = 'UNKNOWN'
    user = os.environ.get('USER', os.environ.get('USERNAME', ukn))
    if user == ukn and hasattr(os, 'getlogin'):
        user = os.getlogin()


class GeniusBotChatTab(QWidget):
    def __init__(self, console):
        super(GeniusBotChatTab, self).__init__()
        self.console = console
        self.geniusbot_chatbot = ChatBot()
        self.geniusbot_chat_tab = QWidget()
        self.geniusbot_chat = ScrollLabel(self)
        self.geniusbot_chat.hide()
        self.geniusbot_chat.setFontColor(background_color="white", color="black")
        self.geniusbot_chat.setText(
            f"""[Genius Bot] Hello there, my name is Geniusbot, I am here to assist you with several things! 
            Explore the tabs at the top to see what I can do!""")
        self.chat_editor = QTextEdit()
        self.chat_editor.installEventFilter(self)
        self.geniusbot_send_button = QPushButton("Send")
        self.geniusbot_send_button.setStyleSheet(
            f"background-color: {blue}; color: white; font: bold; font-size: 14pt;")
        self.geniusbot_send_button.clicked.connect(self.geniusbot_chat_response)
        self.chat_editor.setDisabled(False)
        layout = QVBoxLayout()
        layout.addWidget(self.geniusbot_chat)
        layout.addWidget(self.chat_editor)
        layout.addWidget(self.geniusbot_send_button)
        layout.setStretch(0, 24)
        layout.setStretch(1, 3)
        layout.setStretch(2, 1)
        self.geniusbot_chat_tab.setLayout(layout)

    def geniusbot_chat_response(self):
        print("Sending Chat!!!!!!!!!")
        text = str(self.chat_editor.toPlainText().strip())
        self.geniusbot_chat.setText(f"""{self.geniusbot_chat.text()}\n[{user}] {text}""")
        self.chat_editor.setText("")
        self.geniusbot_thread = QThread()
        self.geniusbot_worker = GeniusBotWorker(geniusbot_chatbot=self.geniusbot_chatbot,
                                                geniusbot_chat=self.geniusbot_chat,
                                                text=text)
        self.geniusbot_worker.moveToThread(self.geniusbot_thread)
        self.geniusbot_thread.started.connect(self.geniusbot_worker.run)
        self.geniusbot_worker.finished.connect(self.geniusbot_thread.quit)
        self.geniusbot_worker.finished.connect(self.geniusbot_worker.deleteLater)
        self.geniusbot_thread.finished.connect(self.geniusbot_thread.deleteLater)
        self.geniusbot_thread.finished.connect(lambda: self.geniusbot_send_button.setDisabled(False))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setDisabled(False))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setText(""))
        self.geniusbot_thread.finished.connect(lambda: self.chat_editor.setFocus())
        self.geniusbot_thread.start()


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