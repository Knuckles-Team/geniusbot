#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import getopt
import requests
import youtube_dl


class VideoDownloader:
    SAVE_PATH = "~/"
    # Link of the video to be downloaded stored in this file path
    links = []

    def __init__(self):
        print("init")

    def open_file(self):
        youtube_urls = open('links_file.txt', 'r')
        for url in youtube_urls:
            self.links.append(url)
        self.links = list(dict.fromkeys(self.links))

    def get_save_path(self):
        return self.SAVE_PATH

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')

    def reset_links(self):
        print("Links Reset")
        self.links = []

    def extend_link(self, urls):
        print("URL Extended: ", urls)
        self.links.extend(urls)
        self.links = list(dict.fromkeys(self.links))

    def append_link(self, url):
        print("URL Appended: ", url)
        self.links.append(url)
        self.links = list(dict.fromkeys(self.links))

    def download_video(self, link):
        ydl_opts = {
           #'format': '22',
           'outtmpl': f'{self.SAVE_PATH}/%(uploader)s - %(title)s.%(ext)s'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            print('Video Downloaded!')
        except Exception as e:
            print(f"Unable to download video: {link}")

    def download_videos(self):
        ydl_opts = {
           'format': '22',
           'outtmpl': f'{self.SAVE_PATH}/%(uploader)s - %(title)s.%(ext)s'
        }
        for link in self.links:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        print('Video Downloaded!')


    def get_channel_videos(self, channel, limit=-1):
        vids = None
        username = channel
        attempts = 0
        while attempts < 3:
            url = f"https://www.youtube.com/user/{username}/videos"
            page = requests.get(url).content
            data = str(page).split(' ')
            item = 'href="/watch?'
            vids = [line.replace('href="', 'youtube.com') for line in data if
                    item in line]  # list of all videos listed twice
            # print(vids)  # index the latest video
            x = 0
            if vids:
                # print("Link Set")
                for vid in vids:
                    if limit < 0:
                        self.links.append(vid)
                    elif x >= limit:
                        break
                    else:
                        self.links.append(vid)
                    x += 1
            else:
                url = f"https://www.youtube.com/channel/{channel}/videos"
                print("URL: ", url)
                page = requests.get(url).content
                print("Page: ", page)
                data = str(page).split(' ')
                print("Data: ", data)
                item = 'https://i.ytimg.com/vi/'
                vids = []
                for line in data:
                    if item in line:
                        vid = line
                        #vid = line.replace('https://i.ytimg.com/vi/', '')
                        try:
                            found = re.search('https://i.ytimg.com/vi/(.+?)/hqdefault.', vid).group(1)
                        except AttributeError:
                            # AAA, ZZZ not found in the original string
                            found = ''  # apply your error handling
                        print("Vid, ", vid)
                        vid = f"https://www.youtube.com/watch?v={found}"
                        vids.append(vid)
                print(vids)  # index the latest video
                x = 0
                if vids:
                    # print("Link Set")
                    for vid in vids:
                        if limit < 0:
                            self.links.append(vid)
                        elif x >= limit:
                            break
                        else:
                            self.links.append(vid)
                        x += 1
                else:
                    print("Trying Old Method")
                    vids = [line.replace('href="', 'youtube.com') for line in data if
                            item in line]  # list of all videos listed twice
                    if vids:
                        for vid in vids:
                            if limit < 0:
                                self.links.append(vid)
                            elif x >= limit:
                                break
                            else:
                                self.links.append(vid)
                            x += 1
                    else:
                        print("Could not find User or Channel")
            attempts += 1


def videodownloader(argv):
    filename = "./links.txt"
    videodownloader = VideoDownloader()
    try:
        opts, args = getopt.getopt(argv, "hc", ["help", "clean"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean_flag = True


def usage():
    print(f'Usage:\n'
          f'-h | --help      [ See usage ]\n'
          f'-c | --clean     [ Convert mobile sites to regular site ]\n'
          f'-d | --directory [ Location where the images will be saved ]\n'
          f'     --dpi       [ DPI for the image ]\n'
          f'-f | --file      [ Text file to read the URLs from ]\n'
          f'-l | --links     [ Comma separated URLs (No spaces) ]\n'
          f'-t | --type      [ Save images as PNG or JPEG ]\n'
          f'-z | --zoom      [ The zoom to use on the browser ]\n'
          f'\n'
          f'videodownloader -c -f <links_file.txt> '
          '-l "<URL1,URL2,URL3>" -t <JPEG/PNG> -d "~/Downloads" -z 100 --dpi 1\n')


def main():
    videodownloader(sys.argv[1:])


if __name__ == "__main__":
    videodownloader(sys.argv[1:])