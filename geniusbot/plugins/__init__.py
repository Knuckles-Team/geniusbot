#!/usr/bin/env python
# coding: utf-8
import sys
sys.path.append("..")
from plugins.subshift_plugin import subshift_tab, SubshiftWorker
from plugins.media_downloader_plugin import media_downloader_tab, MediaDownloaderWorker
from plugins.media_manager_plugin import media_manager_tab, MediaManagerWorker
from plugins.report_manager_plugin import report_manager_tab, ReportManagerWorker, MergeReportWorker