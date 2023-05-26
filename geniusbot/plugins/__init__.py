#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("..")
from plugins.subshift_plugin import subshift_tab, SubshiftWorker
from plugins.media_downloader_plugin import media_downloader_tab, MediaDownloaderWorker
from plugins.media_manager_plugin import media_manager_tab, MediaManagerWorker
from plugins.report_manager_plugin import report_manager_tab, ReportManagerWorker, MergeReportWorker
from plugins.repository_manager_plugin import repository_manager_tab, RepositoryManagerWorker
from plugins.geniusbot_chat_plugin import GeniusBotWorker
from plugins.systems_manager_plugin import systems_manager_tab, SystemsManagerWorker
from plugins.webarchiver_plugin import webarchiver_tab, \
    WebarchiverWorker, \
    screenshot_websites, \
    open_webfile, \
    save_web_location


