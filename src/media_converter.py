#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import re
import subprocess
import urllib.request

import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, COMM


class MediaConverter:
    # Save Location
    SAVE_PATH = None
    OS_SAVE_PATH = None
    CHANNEL_SAVE_PATH = None
    num_cores = None
    inputs = None
    album_art_dir = ""
    # Link of the video to be downloaded stored in this file path
    link = []
    # Create empty YouTube object in case failure of try statement
    yt = None
    title_clean = ""
    description_clean = ""
    author_clean = ""
    ffmpeg = ""
    log = None
    logging_file = ""
    packaged_ffmpeg = "ffmpeg"

    def __init__(self, logger=None):
        # Create and configure logger
        if logger:
            self.log = logger
        else:
            self.log = None
            # self.log = Log()

        self.log.info("YouTube Download: Initialized")
        self.num_cores = 2
        self.set_save_path(os.getcwd())
        print("INIT CWD: ", self.SAVE_PATH)
        self.import_ffmpeg()

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')
        self.set_os_save_path()
        self.log.info(str("Save Path Changed to: ")+str(self.set_os_save_path))

    def set_os_save_path(self):
        self.OS_SAVE_PATH = self.SAVE_PATH.replace('/', os.sep)
        print("OS PATH: ",  self.OS_SAVE_PATH)

    def import_ffmpeg(self):
        if platform.system() == "Windows":
            self.ffmpeg = str(os.path.abspath(os.pardir)) + "/lib/ffmpeg/bin/ffmpeg.exe"
            self.ffmpeg = self.ffmpeg.replace('/', os.sep)
            print("FFMPEG Location on Local", self.ffmpeg)
            if os.path.isfile(self.ffmpeg):
                print("Found!!!!")
                self.log.info(f'Found ffmpeg at: {self.ffmpeg}')
                self.packaged_ffmpeg = self.ffmpeg
            else:
                self.ffmpeg = f"{os.curdir}/lib/ffmpeg/bin/ffmpeg.exe"
                if os.path.isfile(self.ffmpeg):
                    print("Found!!!!")
                    self.packaged_ffmpeg = self.ffmpeg
                    self.log.info(f'Found ffmpeg at: {self.ffmpeg}')
                else:
                    print("Could not find ffmpeg on windows, defaulting to pre-installed ffmpeg")
                    self.log.info(f'Could not find ffmpeg at: {self.ffmpeg}\nUsing Pre-built ffmpeg instead')
                    self.packaged_ffmpeg = "ffmpeg"
        else:
            self.packaged_ffmpeg = "ffmpeg"

    @staticmethod
    def install_ffmpeg():
        print("Install FFMPEG CMD")
        cmd = f'sudo apt-get install ffmpeg -y'
        print("CMD: ", cmd)
        muxing_process = subprocess.Popen(cmd, shell=True)
        muxing_process.wait()

    # quality accepts an integer in a string
    def convert_media(self, media_type, quality="320"):
        # This is for future development to get adaptive files and merge them for higher quality backups
        cmd = f'{self.packaged_ffmpeg} -y -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + str(media_type)}" -b:a {quality}K -vn "{str(self.CHANNEL_SAVE_PATH) + "/" + self.title_clean + ".mp3"}"'
        cmd = cmd.replace('/', os.sep)
        '''if platform.system() == "Linux":
            cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH) + "/" + str(self.title_clean) + str(audio_type)}" -b:a 320K -vn "{str(self.SAVE_PATH) + "/" + self.title_clean + ".mp3"}"'
        else:
            cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH)}\\{str(self.title_clean) + str(audio_type)}" -b:a 320K -vn "{str(self.SAVE_PATH)}\\{self.title_clean + ".mp3"}"'''
        print("CMD: ", cmd)
        muxing_audio = subprocess.Popen(cmd, shell=True)
        muxing_audio.wait()
        print("Waiting for Command to Finish")
        music_dir = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + ".mp3"
        '''if platform.system() == "Linux":
            music_dir = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + ".mp3"
        else:
            music_dir = str(self.SAVE_PATH) + "\\" + str(self.title_clean) + ".mp3"'''
        if os.path.isfile(music_dir):
            print('Merging Done Adding ID3 Tag Info')
            audio_file = EasyID3(str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + ".mp3")
            audio_file['artist'] = self.yt.author
            audio_file['title'] = self.yt.title
            audio_file.save()
            audio_file = ID3(str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + ".mp3")
            print("Thumbnail URL: ", self.album_art_dir)
            with open(self.album_art_dir, 'rb') as album_art:
                print("Album Art: ", album_art)
                '''if album_art.endswith('png'):
                    mime = 'image/png'
                else:
                    mime = 'image/jpeg'''''
                audio_file['APIC'] = APIC(encoding=3,
                                          mime='image/jpeg',
                                          type=3, desc=u'Front Cover',
                                          data=album_art.read())
                audio_file['COMM'] = COMM(encoding=3, text=self.yt.description)
                audio_file.save()
        else:
            return -1