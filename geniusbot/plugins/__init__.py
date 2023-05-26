#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("..")
from plugins.subshift_plugin import initialize_subshift_tab, SubshiftWorker
from plugins.media_downloader_plugin import initialize_media_downloader_tab, MediaDownloaderWorker
from plugins.media_manager_plugin import initialize_media_manager_tab, MediaManagerWorker
from plugins.report_manager_plugin import initialize_report_manager_tab, ReportManagerWorker, MergeReportWorker
from plugins.repository_manager_plugin import initialize_repository_manager_tab, RepositoryManagerWorker
from plugins.geniusbot_chat_plugin import GeniusBotWorker, initialize_geniusbot_chat_tab
from plugins.systems_manager_plugin import initialize_systems_manager_tab, SystemsManagerWorker
from plugins.webarchiver_plugin import initialize_webarchiver_tab, \
    WebarchiverWorker, \
    screenshot_websites, \
    open_webfile, \
    save_web_location


