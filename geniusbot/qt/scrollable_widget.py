#!/usr/bin/env python3

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class ScrollLabel(QScrollArea):
    """Scrollable label widget using PySide6."""

    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setStyleSheet("background-color: #211f1f;")

        self.scroll_bar = self.verticalScrollBar()
        self.setWidgetResizable(True)

        content = QWidget(self)
        self.setWidget(content)

        lay = QVBoxLayout(content)

        self.label = QLabel(content)
        self.label.setFont(QFont("Monospace", 10))
        self.label.setStyleSheet("background-color: #211f1f; color: white;")
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)

        lay.addWidget(self.label)
        self.setHidden(True)

    def setFont(self, font="Monospace"):
        self.label.setFont(QFont(font, 10))

    def setFontColor(self, background_color="#211f1f", color="white"):
        self.label.setStyleSheet(
            f"background-color: {background_color}; color: {color};"
        )
        self.setStyleSheet(f"background-color: {background_color};")

    def setText(self, text):
        self.label.setText(text)

    def setScrollWheel(self, location="Top"):
        if location == "Bottom":
            self.scroll_bar.rangeChanged.connect(
                lambda: self.scroll_bar.setValue(self.scroll_bar.maximum())
            )
        else:
            self.scroll_bar.rangeChanged.connect(lambda: self.scroll_bar.setValue(0))

    def text(self):
        return self.label.text()

    def hide(self):
        if self.isHidden():
            self.setHidden(False)
        else:
            self.setHidden(True)
