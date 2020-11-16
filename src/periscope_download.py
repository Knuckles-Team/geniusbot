#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import re
import sys
import urllib.request
import pyriscope

from subprocess import Popen, PIPE
from src.log import Log

import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, COMM


class PeriscopeDownloader:
    if os.name == 'nt':
        SAVE_PATH = f'C:\\Users\\{os.getlogin()}\\Downloads'
    else:
        home = os.path.expanduser("~")
        SAVE_PATH = os.path.join(home, "Downloads")
    OS_SAVE_PATH = SAVE_PATH
    CHANNEL_SAVE_PATH = None
    num_cores = None
    inputs = None
    album_art_dir = ""
    # Link of the video to be downloaded stored in this file path
    link = []
    # Create empty YouTube object in case failure of try statement
    periscope = None
    title_clean = ""
    description_clean = ""
    author_clean = ""
    log = None
    logging_file = ""

    def __init__(self, logger=None):
        # Create and configure logger
        if logger:
            self.log = logger
        else:
            #self.log = None
            self.log = Log()
            self.log.init_logging()

        self.log.info("Periscope Download: Initialized")
        self.num_cores = 2
        self.set_save_path(self.SAVE_PATH)
        print("INIT CWD: ", self.SAVE_PATH)

    def open_file(self):
        periscope_urls = open('links_file.txt', 'r')
        print("periscope_urls", periscope_urls)
        # self.log.info(str("YouTube URLs: ")+youtube_urls)
        self.log.info(str("Length of Links Before Open File: ")+str(len(self.link)))
        print("Length of Links Before Open File: ", len(self.link))
        for url in periscope_urls:
            self.link.append(url)
        self.link = list(dict.fromkeys(self.link))
        print("Length of Links After Open File: ", len(self.link))
        self.log.info(str("Length of Links After Open File: ")+str(len(self.link)))

    def get_link(self):
        self.link = list(dict.fromkeys(self.link))
        return self.link

    def get_save_path(self):
        return self.SAVE_PATH

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')
        self.set_os_save_path()
        self.log.info(str("Save Path Changed to: ")+str(self.set_os_save_path))

    def set_os_save_path(self):
        self.OS_SAVE_PATH = self.SAVE_PATH.replace('/', os.sep)
        print("OS PATH: ",  self.OS_SAVE_PATH)

    def set_channel_save_path(self, channel):
        self.CHANNEL_SAVE_PATH = str(self.SAVE_PATH) + '/' + str(channel)
        print("CHANNEL_SAVE_PATH: ",  self.CHANNEL_SAVE_PATH)
        self.CHANNEL_SAVE_PATH = self.CHANNEL_SAVE_PATH.replace('/', os.sep)

    def reset_links(self):
        print("Links Reset")
        self.log.info("Links Reset")
        self.link = []

    def extend_link(self, urls):
        print("URL Extended: ", urls)
        self.link.extend(urls)
        self.link = list(dict.fromkeys(self.link))

    def append_link(self, url):
        print("URL Appended: ", url)
        self.link.append(url)
        self.link = list(dict.fromkeys(self.link))

    # This will make a directory for the videos being Downloaded
    def make_video_directory(self):
        print("Directory to be created: ", self.CHANNEL_SAVE_PATH)
        if self.title_clean != "":
            self.set_channel_save_path(self.title_clean)
            try:
                # Create target Directory
                os.mkdir(self.CHANNEL_SAVE_PATH)
                print("Directory ", self.CHANNEL_SAVE_PATH, " created ")
                self.log.info(f'Directory {self.CHANNEL_SAVE_PATH} created')
            except FileExistsError:
                print("Directory ", self.CHANNEL_SAVE_PATH, " already exists")
                self.log.info(f'Directory {self.CHANNEL_SAVE_PATH} already exists')

    def download_videos(self):
        # Clean Duplicates First
        self.link = list(dict.fromkeys(self.link))
        # Iterate over all the links
        for i in self.link:
            # Create Directory for Videos about to be downloaded
            self.make_video_directory()

            # Video Downloaded
            print(f"Links: {self.link}")
            args = ["--clean"]
            for link in self.link:
                args.append(link)
            #args.extend("some additional command".split())
            print(f"args {args}")
            p = Popen([pyriscope] + args, stdout=PIPE)
            p.stdout.close()
            p.wait()

# Usage
if __name__ == "__main__":
    # Create Object
    test = PeriscopeDownloader()

    #
    test.append_link("https://www.pscp.tv/darrenrovell/1nAKEVALjVnGL")
    test.append_link("https://www.pscp.tv/w/1BdGYYjgkgQGX")
    #
    test.download_videos()