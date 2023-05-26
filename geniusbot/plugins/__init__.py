#!/usr/bin/env python
# coding: utf-8

try:
    from geniusbot.plugins.webarchiver_plugin import webarchiver_tab, screenshot_websites, open_webfile, save_web_location, WebarchiverWorker
    from geniusbot.plugins.geniusbot_plugin import GeniusBotWorker
except Exception:
    from plugins.webarchiver_plugin import webarchiver_tab, screenshot_websites, open_webfile, save_web_location, WebarchiverWorker
    from plugins.geniusbot_chat_plugin import GeniusBotWorker

