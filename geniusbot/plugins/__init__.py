#!/usr/bin/env python
# coding: utf-8

try:
    from plugins.subshift_plugin import SubshiftTab, SubshiftWorker
except:
    from geniusbot.plugins.subshift_plugin import SubshiftTab, SubshiftWorker
try:
    from plugins.media_downloader_plugin import MediaDownloaderTab, MediaDownloaderWorker
except:
    from geniusbot.plugins.media_downloader_plugin import MediaDownloaderTab, MediaDownloaderWorker
try:
    from plugins.media_manager_plugin import MediaManagerTab, MediaManagerWorker
except:
    from geniusbot.plugins.media_manager_plugin import MediaManagerTab, MediaManagerWorker
try:
    from plugins.report_manager_plugin import ReportManagerTab, ReportManagerWorker, MergeReportWorker
except:
    from geniusbot.plugins.report_manager_plugin import ReportManagerTab, ReportManagerWorker, MergeReportWorker
try:
    from plugins.repository_manager_plugin import RepositoryManagerTab, RepositoryManagerWorker
except:
    from geniusbot.plugins.repository_manager_plugin import RepositoryManagerTab, RepositoryManagerWorker
try:
    from plugins.geniusbot_chat_plugin import GeniusBotWorker, GeniusBotChatTab
except:
    from geniusbot.plugins.geniusbot_chat_plugin import GeniusBotWorker, GeniusBotChatTab
try:
    from plugins.systems_manager_plugin import SystemsManagerTab, SystemsManagerWorker
except:
    from geniusbot.plugins.systems_manager_plugin import SystemsManagerTab, SystemsManagerWorker
try:
    from plugins.webarchiver_plugin import WebarchiverTab, WebarchiverWorker
except:
    from geniusbot.plugins.webarchiver_plugin import WebarchiverTab, WebarchiverWorker
