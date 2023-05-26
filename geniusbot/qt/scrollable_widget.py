#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QScrollArea
)
from PyQt5.QtGui import QFont


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