#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("..")
from plugins.subshift_plugin import SubshiftTab, SubshiftWorker
from plugins.media_downloader_plugin import MediaDownloaderTab, MediaDownloaderWorker
from plugins.media_manager_plugin import MediaManagerTab, MediaManagerWorker
from plugins.report_manager_plugin import ReportManagerTab, ReportManagerWorker, MergeReportWorker
from plugins.repository_manager_plugin import RepositoryManagerTab, RepositoryManagerWorker
from plugins.geniusbot_chat_plugin import GeniusBotWorker, GeniusBotChatTab
from plugins.systems_manager_plugin import SystemsManagerTab, SystemsManagerWorker
from plugins.webarchiver_plugin import WebarchiverTab, WebarchiverWorker

