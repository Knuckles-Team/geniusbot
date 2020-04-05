from genius_bot import App
from youtube_download import YouTubeDownloader
import tkinter as tk
import threading
import time
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import os
import urllib.request
import json
import shutil
import requests
import subprocess
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, COMM
from mutagen.flac import Picture
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
import time


class Controller:
    app = None
    ytd = None
    def __init__(self):
        print("Initialized")
        # self.num_cores = multiprocessing.cpu_count()
        self.num_cores = 2
        self.app = App()
        print('Now we can continue running code while mainloop runs!')
        self.ytd = YouTubeDownloader()

    def setYouTubeDownloader(self):
        start = time.process_time()
        # youtube_connector.open_file()
        list = self.app.get_links()
        self.ytd.append_link('https://www.youtube.com/watch?v=Xq-knHXSKYY')
        # youtube_connector.get_channel_videos('UCXcnHuosOLaKOGU0qQoYzfA')
        print("Youtube Links: ", self.ytd.get_link())
        print("Length Youtube Links: ", len(self.ytd.get_link()))
        # youtube_connector.download_hd_videos_parallel()
        self.ytd.download_hd_videos()
        print("Executed Seconds: ", (time.process_time() - start))
        # youtube_connector.download_audio()

main()
