#!/usr/bin/env python
# coding: utf-8
from geniusbot.version import __version__, __author__, __credits__
from geniusbot.geniusbot import geniusbot, GeniusBot
from geniusbot.plugins import \
    geniusbot_chat_plugin, \
    media_downloader_plugin, \
    media_manager_plugin, \
    report_manager_plugin, \
    repository_manager_plugin, \
    subshift_plugin, \
    systems_manager_plugin, \
    webarchiver_plugin
from geniusbot.qt.scrollable_widget import ScrollLabel
from geniusbot.qt import colors
from geniusbot.qt.colors import yellow, green, orange, blue, red, purple


"""
geniusbot

A tool that does it all!
"""

__version__ = __version__
__author__ = __author__
__credits__ = __credits__
colors = colors
yellow = yellow
green = green
orange = orange
blue = blue
red = red
purple = purple
