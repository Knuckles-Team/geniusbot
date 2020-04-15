import os
import platform
import re
import subprocess
import urllib.request
#importing module
import logging

import requests
#from joblib import Parallel, delayed
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, COMM
from pytube import YouTube
#from tqdm import tqdm


class YouTubeDownloader:
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
    logger = None
    logging_file = ""

    def __init__(self):
        #Create and configure logger
        self.logging_file = f"{os.pardir}/logs/usage_history.log"
        if os.path.isfile(self.logging_file):
            print("Usage File: ",  self.logging_file)
        else:
            self.logging_file = f"{os.curdir}/logs/usage_history.log"
            print("Usage File: ",  self.logging_file)
        logging.basicConfig(filename=self.logging_file, format='%(asctime)s %(message)s', filemode='w')
        #Creating an object
        self.logger=logging.getLogger()
        #Setting the threshold of logger to DEBUG
        self.logger.setLevel(logging.DEBUG)
        #Test messages
        self.logger.debug("Debug: Initialized")
        self.logger.info("Info: Initialized")
        self.logger.warning("Warning: Initialized")
        self.logger.error("Error: Initialized")
        self.logger.critical("Critical: Initialized")
        self.num_cores = 2
        self.set_save_path(os.getcwd())
        print("INIT CWD: ", self.SAVE_PATH)
        self.import_ffmpeg()


    def open_file(self):
        youtube_urls = open('links_file.txt', 'r')
        print("youtube_urls", youtube_urls)
        #self.logger.info(str("YouTube URLs: ")+youtube_urls)
        self.logger.info(str("Length of Links Before Open File: ")+str(len(self.link)))
        print("Length of Links Before Open File: ", len(self.link))
        for url in youtube_urls:
            self.link.append(url)
        self.link = list(dict.fromkeys(self.link))
        print("Length of Links After Open File: ", len(self.link))
        self.logger.info(str("Length of Links After Open File: ")+str(len(self.link)))

    def get_link(self):
        self.link = list(dict.fromkeys(self.link))
        return self.link

    def get_save_path(self):
        return self.SAVE_PATH

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')
        self.set_os_save_path()
        self.logger.info(str("Save Path Changed to: ")+str(self.set_os_save_path))

    def set_os_save_path(self):
        self.OS_SAVE_PATH = self.SAVE_PATH.replace('/', os.sep)
        print("OS PATH: ",  self.OS_SAVE_PATH)

    def set_channel_save_path(self, channel):
        self.CHANNEL_SAVE_PATH = str(self.SAVE_PATH) + '/' + str(channel)
        print("CHANNEL_SAVE_PATH: ",  self.CHANNEL_SAVE_PATH)
        self.CHANNEL_SAVE_PATH = self.CHANNEL_SAVE_PATH.replace('/', os.sep)

    def reset_links(self):
        print("Links Reset")
        self.logger.info("Links Reset")
        self.link = []

    def import_ffmpeg(self):
        if platform.system() == "Windows":
            self.ffmpeg = str(os.path.abspath(os.pardir)) + "/lib/ffmpeg/bin/ffmpeg.exe"
            self.ffmpeg = self.ffmpeg.replace('/', os.sep)
            print("FFMPEG Location on Local", self.ffmpeg)
            if os.path.isfile(self.ffmpeg):
                print("Found!!!!")
                self.logger.info(f'Found ffmpeg at: {self.ffmpeg}')
                self.packaged_ffmpeg = self.ffmpeg
            else:
                self.ffmpeg = f"{os.curdir}/lib/ffmpeg/bin/ffmpeg.exe"
                if os.path.isfile(self.ffmpeg):
                    print("Found!!!!")
                    self.packaged_ffmpeg = self.ffmpeg
                    self.logger.info(f'Found ffmpeg at: {self.ffmpeg}')
                else:
                    print("Could not find ffmpeg on windows, defaulting to pre-installed ffmpeg")
                    self.logger.info(f'Could not find ffmpeg at: {self.ffmpeg}\nUsing Pre-built ffmpeg instead')
                    self.packaged_ffmpeg = "ffmpeg"
        else:
            self.packaged_ffmpeg = "ffmpeg"


    def install_ffmpeg(self):
        print("Install FFMPEG CMD")
        cmd = f'sudo apt-get install ffmpeg -y'
        #cmd = cmd.replace('/', os.sep)
        print("CMD: ", cmd)
        muxing_process = subprocess.Popen(cmd, shell=True)
        muxing_process.wait()

    def install_tcl_thread(self):
        print("Install thread by running command")

    def extend_link(self, urls):
        print("URL Extended: ", urls)
        self.link.extend(urls)
        self.link = list(dict.fromkeys(self.link))

    def append_link(self, url):
        print("URL Appended: ", url)
        self.link.append(url)
        self.link = list(dict.fromkeys(self.link))

    # This will make a directory for the videos being Downloaded
    def make_channel_directory(self):
        self.set_channel_save_path(self.author_clean)
        '''if platform.system() == "Linux":
            self.SAVE_PATH = f'{str(self.SAVE_PATH)}/{str(self.author_clean)}'
        else:
            self.SAVE_PATH = f'{str(self.SAVE_PATH)}\\{str(self.author_clean)}'''
        print("Directory to be created: ", self.CHANNEL_SAVE_PATH)
        if self.author_clean != "":
            try:
                # Create target Directory
                os.mkdir(self.CHANNEL_SAVE_PATH)
                print("Directory ", self.CHANNEL_SAVE_PATH, " created ")
                self.logger.info(f'Directory {self.CHANNEL_SAVE_PATH} created')
            except FileExistsError:
                print("Directory ", self.CHANNEL_SAVE_PATH, " already exists")
                self.logger.info(f'Directory {self.CHANNEL_SAVE_PATH} already exists')

    # This class uses ffmpeg to merge the hd video and hd audio together
    def merge_video_audio(self, vid_type, aud_type, output_type=".webm"):
        print("vid type: ", vid_type)
        if vid_type == ".webm":
            # This is for future development to get adaptive files and merge them for higher quality backups
            cmd = f'{self.packaged_ffmpeg} -y -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v copy -c:a copy -metadata title="{self.title_clean}" -metadata description="Duration{self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.CHANNEL_SAVE_PATH) + "/" + self.title_clean + str(output_type)}"'
            cmd = cmd.replace('/', os.sep)
        else:
            cmd = f'{self.packaged_ffmpeg} -y -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v libx264 -metadata title="{self.title_clean}" -metadata description="Duration {self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.CHANNEL_SAVE_PATH) + "/" + self.title_clean + str(output_type)}"'
            cmd = cmd.replace('/', os.sep)
        '''if platform.system() == "Linux":
            if vid_type == ".webm":
                # This is for future development to get adaptive files and merge them for higher quality backups
                cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v copy -c:a copy -metadata title="{self.title_clean}" -metadata description="Duration{self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.SAVE_PATH) + "/" + self.title_clean + str(output_type)}"'
            else:
                cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v libx264 -metadata title="{self.title_clean}" -metadata description="Duration {self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.SAVE_PATH) + "/" + self.title_clean + str(output_type)}"'
        else:
            if vid_type == ".webm":
                # This is for future development to get adaptive files and merge them for higher quality backups
                cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH)}\\{str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.SAVE_PATH)}\\{str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v copy -c:a copy -metadata title="{self.title_clean}" -metadata description="Duration{self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.SAVE_PATH)}\\{self.title_clean + str(output_type)}"'
            else:
                cmd = f'ffmpeg -y -i "{str(self.SAVE_PATH)}\\{str(self.title_clean) + "_video_dl" + str(vid_type)}" -i "{str(self.SAVE_PATH)}\\{str(self.title_clean) + "_audio_dl" + str(aud_type)}" -c:v libx264 -metadata title="{self.title_clean}" -metadata description="Duration {self.yt.length} Views {self.yt.views} Description {self.description_clean}" -metadata language={"English"} "{str(self.SAVE_PATH)}\\{self.title_clean + str(output_type)}"'
        '''
        print("CMD: ", cmd)
        muxing_process = subprocess.Popen(cmd, shell=True)
        muxing_process.wait()
        temporary_check = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + str(vid_type)
        temporary_check = temporary_check.replace('/', os.sep)
        if os.path.isfile(temporary_check):
            print('Merging Done')
        else:
            return -1

    def convert_mp3(self, audio_type):
        # This is for future development to get adaptive files and merge them for higher quality backups
        cmd = f'{self.packaged_ffmpeg} -y -i "{str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + str(audio_type)}" -b:a 320K -vn "{str(self.CHANNEL_SAVE_PATH) + "/" + self.title_clean + ".mp3"}"'
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

    def download_hd_videos(self):
        # Clean Duplicates First
        self.link = list(dict.fromkeys(self.link))
        # Iterate over all the links
        for i in self.link:
            attempts = 0
            # Try 3 times to pull a video
            while attempts < 3:
                try:
                    # object creation using YouTube which was imported in the beginning
                    print("Downloading Link: ", i)
                    self.yt = YouTube(i)
                    print("Youtube Title: ", self.yt.title)
                    # print(self.yt.streams)
                    if self.yt.title == "YouTube":
                        print("Title is YouTube, retrying")
                    else:
                        print("Saving Video: ", self.yt.title)
                        self.title_clean = re.sub(r'[^A-Za-z0-9_]', '', self.yt.title.replace(" ", "_"))
                        self.description_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.description.replace("\n", ""))
                        self.author_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.author.replace("\n", ""))
                        print("Clean Author: ", self.author_clean)
                        print("Clean Title ", self.title_clean)
                        break
                except:
                    attempts += 1
                    print("Connection Error: Attempt ", attempts)  # to handle exception

            # Create Directory for Videos about to be downloaded
            self.make_channel_directory()
            # Filters out all the files with "mp4" extension and media with audio and video combined.
            # Progressive - Audio and Video merged vs Adaptive - Audio and Video Separate
            video_type = ".webm"
            audio_type = ".webm"
            webm_video = None
            mp4_video = None
            webm_audio = None
            mp4_audio = None
            try:
                webm_video = self.yt.streams.filter(progressive=False, file_extension='webm', only_video=True)
            except AttributeError as e:
                print("Error in Reading YouTube Stream, retrying....")
                try:
                    webm_video = self.yt.streams.filter(progressive=False, file_extension='webm', only_video=True)
                except AttributeError as e:
                    print("Error in Reading YouTube Stream")
            try:
                mp4_video = self.yt.streams.filter(progressive=False, file_extension='mp4', only_video=True)
            except AttributeError as e:
                print("Error in Reading YouTube Stream, retrying....")
                try:
                    mp4_video = self.yt.streams.filter(progressive=False, file_extension='mp4', only_video=True)
                except AttributeError as e:
                    print("Error in Reading YouTube Stream")
            try:
                webm_audio = self.yt.streams.filter(progressive=False, file_extension='webm', only_audio=True)
            except AttributeError as e:
                print("Error in Reading YouTube Stream, retrying....")
                try:
                    webm_audio = self.yt.streams.filter(progressive=False, file_extension='webm', only_audio=True)
                except AttributeError as e:
                    print("Error in Reading YouTube Stream")
            try:
                mp4_audio = self.yt.streams.filter(progressive=False, file_extension='mp4', only_audio=True)
            except AttributeError as e:
                print("Error in Reading YouTube Stream, retrying....")
                try:
                    mp4_audio = self.yt.streams.filter(progressive=False, file_extension='mp4', only_audio=True)
                except AttributeError as e:
                    print("Error in Reading YouTube Stream")
            if webm_video:
                print("Entered Webm Video")
                webm_video = webm_video.order_by("resolution").last()
            if mp4_video:
                print("Entered mp4 Video")
                mp4_video = mp4_video.order_by("resolution").last()
            if webm_audio:
                print("Entered Webm Audio")
                webm_audio = webm_audio.order_by("bitrate").last()
            if mp4_audio:
                print("Entered mp4 Audio")
                mp4_audio = mp4_audio.order_by("bitrate").last()

            save_attempts_video = 0
            save_attempts_video_mp4 = 0
            # Try 3 times to pull a video
            while save_attempts_video < 3:
                # downloading the video
                try:
                    print("Downloading Video")
                    webm_video.download(output_path=self.CHANNEL_SAVE_PATH, filename="_video_dl", filename_prefix=self.title_clean)
                    save_attempts_video_mp4 = 3
                    break
                except:
                    save_attempts_video += 1
                    print("Some WEBM Video Error!")
            while save_attempts_video_mp4 < 3:
                # downloading the video
                try:
                    print("Downloading Video")
                    mp4_video.download(output_path=self.CHANNEL_SAVE_PATH, filename="_video_dl", filename_prefix=self.title_clean)
                    video_type = ".mp4"
                    break
                except:
                    save_attempts_video_mp4 += 1
                    print("Some MP4 Video Error!")
            save_attempts_audio = 0
            save_attempts_audio_mp4 = 0
            # downloading the audio
            while save_attempts_audio < 3:
                try:
                    print("Downloading Audio")
                    webm_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename="_audio_dl", filename_prefix=self.title_clean)
                    save_attempts_audio_mp4 = 3
                    break
                except:
                    save_attempts_audio += 1
                    print("Some WEBM Audio Error!")

            while save_attempts_audio_mp4 < 3:
                try:
                    print("Downloading Audio")
                    mp4_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename="_audio_dl", filename_prefix=self.title_clean)
                    audio_type = ".mp4"
                    break
                except:
                    save_attempts_audio_mp4 += 1
                    print("Some MP4 Audio Error!")
            if (save_attempts_video >= 3 and save_attempts_video_mp4 >= 3) or (
                    save_attempts_audio >= 3 and save_attempts_audio_mp4 >= 3):
                print("Failed to download Video or Audio or Both")
            else:
                result = self.merge_video_audio(video_type, audio_type, video_type)
                if result != -1:
                    try:
                        old_video_file = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(video_type)
                        old_video_file = old_video_file.replace('/', os.sep)
                        os.remove(old_video_file)
                        print("Removed Video")
                    except:
                        print("Could not Remove Source Video")
                    try:
                        old_audio_file = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(audio_type)
                        old_audio_file = old_audio_file.replace('/', os.sep)
                        os.remove(old_audio_file)
                        print("Removed Audio")
                    except:
                        print("Could not Remove Source Audio")
                else:
                    print("Could not Merge Two Source Files with FFMpeg")
            self.author_clean=""
        print('Video Downloaded!')

    def download_videos(self):
        # Iterate over all the links
        for i in self.link:
            attempts = 0
            # Try 3 times to pull a video
            while attempts < 3:
                try:
                    # object creation using YouTube which was imported in the beginning
                    print("Downloading Link: ", i)
                    self.yt = YouTube(i)
                    if self.yt.title == "YouTube":
                        print("Title is YouTube, retrying")
                    else:
                        print("Saving Video: ", self.yt.title)
                        self.title_clean = re.sub(r'[^A-Za-z0-9_]', '', self.yt.title.replace(" ", "_"))
                        self.description_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.description.replace("\n", ""))
                        self.author_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.author.replace("\n", ""))
                        print("Clean Title ", self.title_clean)
                        break
                except:
                    attempts += 1
                    print("Connection Error: Attempt ", attempts)  # to handle exception

            self.make_channel_directory()
            # Filters out all the files with "mp4" extension and media with audio and video combined.
            # Progressive - Audio and Video merged vs Adaptive - Audio and Video Separate

            # This version downloads the 720p Video with Audio
            d_video = self.yt.streams.get_by_itag('22')
            print("D_Video ", d_video)
            if d_video:
                print("Good Video")
            else:
                # This version downloads the 360p Video with Audio
                d_video = self.yt.streams.get_by_itag('18')
            save_attempts = 0
            # Try 3 times to pull a video
            while save_attempts < 3:
                try:
                    # downloading the video
                    print("Saving Video")
                    # d_video.download(self.SAVE_PATH)
                    break
                except:
                    save_attempts += 1
                    print("Some Error!")
        print('Task Completed!')

    def download_audio(self):
        # Iterate over all the links
        for i in self.link:
            attempts = 0
            # Try 3 times to pull a video
            while attempts < 3:
                try:
                    # object creation using YouTube which was imported in the beginning
                    print("Downloading Link: ", i)
                    self.yt = YouTube(i)
                    if self.yt.title == "YouTube":
                        print("Title is YouTube, retrying")
                    else:
                        print("Saving Video: ", self.yt.title)
                        self.title_clean = re.sub(r'[^A-Za-z0-9_]', '', self.yt.title.replace(" ", "_"))
                        self.description_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.description.replace("\n", ""))
                        self.author_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.author.replace("\n", ""))
                        print("Clean Title ", self.title_clean)
                        break
                except:
                    attempts += 1
                    print("Connection Error: Attempt ", attempts)  # to handle exception

            self.make_channel_directory()
            self.album_art_dir = str(self.CHANNEL_SAVE_PATH) + "/album_art.jpg"
            self.album_art_dir = self.album_art_dir.replace('/', os.sep)
            '''
            if platform.system() == "Linux":
                self.album_art_dir = str(self.CHANNEL_SAVE_PATH) + "/album_art.jpg"
            else:
                self.album_art_dir = str(self.SAVE_PATH) + "\\album_art.jpg"'''

            urllib.request.urlretrieve(self.yt.thumbnail_url, self.album_art_dir)
            # Filters out all the files with "mp4" extension and media with audio and video combined.
            # Progressive - Audio and Video merged vs Adaptive - Audio and Video Separate
            mp4files = self.yt.streams.filter(progressive=True, file_extension='mp4')

            # This version downloads the 720p Video with Audio
            d_video = self.yt.streams.filter(only_audio=True).order_by("bitrate").last()
            print("D_Video ", d_video)
            if d_video:
                print("Good Audio")
            else:
                # This version downloads the 360p Video with Audio
                print("Could not fetch Audio")
            save_attempts = 0
            # Try 3 times to pull a video
            while save_attempts < 3:
                try:
                    # downloading the video
                    print("Saving Audio")
                    print("Audio Type: ", d_video.parse_codecs())
                    d_video.download(output_path=self.CHANNEL_SAVE_PATH, filename=self.title_clean)
                    break
                except:
                    save_attempts += 1
                    print("Some Error!")

            webm_audio = self.yt.streams.filter(progressive=False, file_extension='webm', only_audio=True).order_by(
                "bitrate").last()
            mp4_audio = self.yt.streams.filter(progressive=False, file_extension='mp4', only_audio=True).order_by(
                "bitrate").last()

            save_attempts_audio = 0
            save_attempts_audio_mp4 = 0
            audio_type = ".webm"
            # downloading the audio
            while save_attempts_audio < 3:
                try:
                    print("Downloading Audio")
                    webm_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename=self.title_clean)
                    audio_type = ".webm"
                    save_attempts_audio_mp4 = 3
                    break
                except:
                    save_attempts_audio += 1
                    print("Some WEBM Audio Error!")

            while save_attempts_audio_mp4 < 3:
                try:
                    print("Downloading Audio")
                    mp4_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename=self.title_clean)
                    audio_type = ".mp4"
                    break
                except:
                    save_attempts_audio_mp4 += 1
                    print("Some MP4 Audio Error!")
            if save_attempts_audio >= 3 and save_attempts_audio_mp4 >= 3:
                print("Failed to download Video or Audio or Both")
            else:
                result = self.convert_mp3(audio_type)
                if result != -1:
                    try:

                        old_audio_file = str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + str(audio_type)
                        old_audio_file = old_audio_file.replace('/', os.sep)
                        old_audio_art = str(self.CHANNEL_SAVE_PATH) + "/album_art.jpg"
                        old_audio_art = old_audio_art.replace('/', os.sep)
                        os.remove(old_audio_file)
                        os.remove(old_audio_art)
                        '''if platform.system() == "Linux":
                            os.remove(str(self.SAVE_PATH) + "/" + str(self.title_clean) + str(audio_type))
                            os.remove(str(self.SAVE_PATH) + "/album_art.jpg")
                        else:
                            os.remove(str(self.SAVE_PATH) + "\\" + str(self.title_clean) + str(audio_type))
                            os.remove(str(self.SAVE_PATH) + "\\album_art.jpg")'''
                        print("Removed Audio")
                    except:
                        print("Could not Remove Source Audio")
                else:
                    print("Could not Merge Two Source Files with FFMpeg")
        print('Task Completed!')

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
            #print(vids)  # index the latest video
            x = 0
            if vids:
                #print("Link Set")
                for vid in vids:
                    if limit < 0:
                        self.link.append(vid)
                    elif x >= limit:
                        break
                    else:
                        self.link.append(vid)
                    x += 1
            else:
                url = f"https://www.youtube.com/channel/{channel}/videos"
                print("URL: ", url)
                page = requests.get(url).content
                data = str(page).split(' ')
                item = 'href="/watch?'
                vids = [line.replace('href="', 'youtube.com') for line in data if
                        item in line]  # list of all videos listed twice
                #print(vids)  # index the latest video
                x = 0
                if vids:
                    #print("Link Set")
                    for vid in vids:
                        if limit < 0:
                            self.link.append(vid)
                        elif x >= limit:
                            break
                        else:
                            self.link.append(vid)
                        x += 1
                        #print("Length of Links: ", len(self.link))
                else:
                    print("Could not find User or Channel")
            attempts += 1
'''
    def download_hd_videos_parallel(self):
        link_list = self.get_link()
        # Clean Duplicates First
        self.link = list(dict.fromkeys(self.link))
        inputs = tqdm(self.link)
        processed_list = Parallel(n_jobs=self.num_cores)(delayed(self.hd_videos_parallel_processor)(i) for i in inputs)
        print("Processed List Complete: ", processed_list)

    def hd_videos_parallel_processor(self, i):
        attempts = 0
        # Try 3 times to pull a video
        while attempts < 3:
            try:
                # object creation using YouTube which was imported in the beginning
                print("Downloading Link: ", i)
                self.yt = YouTube(i)
                # print(self.yt.streams)
                if self.yt.title == "YouTube":
                    print("Title is YouTube, retrying")
                else:
                    print("Saving Video: ", self.yt.title)
                    self.title_clean = re.sub(r'[^A-Za-z0-9_]', '', self.yt.title.replace(" ", "_"))
                    self.description_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.description.replace("\n", ""))
                    self.author_clean = re.sub(r'[^A-Za-z0-9_ ]', '', self.yt.author.replace("\n", ""))
                    print("Clean Title ", self.title_clean)
                    break
            except:
                attempts += 1
                print("Connection Error: Attempt ", attempts)  # to handle exception

        # Filters out all the files with "mp4" extension and media with audio and video combined.
        # Progressive - Audio and Video merged vs Adaptive - Audio and Video Separate
        video_type = ".webm"
        audio_type = ".webm"
        webm_video = self.yt.streams.filter(progressive=False, file_extension='webm', only_video=True).order_by(
                "resolution").last()
        mp4_video = self.yt.streams.filter(progressive=False, file_extension='mp4', only_video=True).order_by(
                "resolution").last()
        webm_audio = self.yt.streams.filter(progressive=False, file_extension='webm', only_audio=True).order_by(
                "bitrate").last()
        mp4_audio = self.yt.streams.filter(progressive=False, file_extension='mp4', only_audio=True).order_by(
                "bitrate").last()
        save_attempts_video = 0
        save_attempts_video_mp4 = 0
        # Try 3 times to pull a video
        while save_attempts_video < 3:
            # downloading the video
            try:
                print("Downloading Video")
                webm_video.download(output_path=self.CHANNEL_SAVE_PATH, filename="_video_dl", filename_prefix=self.title_clean)
                save_attempts_video_mp4 = 3
                break
            except:
                save_attempts_video += 1
                print("Some WEBM Video Error!")

        while save_attempts_video_mp4 < 3:
            # downloading the video
            try:
                print("Downloading Video")
                mp4_video.download(output_path=self.CHANNEL_SAVE_PATH, filename="_video_dl", filename_prefix=self.title_clean)
                video_type = ".mp4"
                break
            except:
                save_attempts_video_mp4 += 1
                print("Some MP4 Video Error!")
        save_attempts_audio = 0
        save_attempts_audio_mp4 = 0
        # downloading the audio
        while save_attempts_audio < 3:
            try:
                print("Downloading Audio")
                webm_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename="_audio_dl", filename_prefix=self.title_clean)
                save_attempts_audio_mp4 = 3
                break
            except:
                save_attempts_audio += 1
                print("Some WEBM Audio Error!")

        while save_attempts_audio_mp4 < 3:
            try:
                print("Downloading Audio")
                mp4_audio.download(output_path=self.CHANNEL_SAVE_PATH, filename="_audio_dl", filename_prefix=self.title_clean)
                audio_type = ".mp4"
                break
            except:
                save_attempts_audio_mp4 += 1
                print("Some MP4 Audio Error!")
        if (save_attempts_video >= 3 and save_attempts_video_mp4 >= 3) or (
                save_attempts_audio >= 3 and save_attempts_audio_mp4 >= 3):
            print("Failed to download Video or Audio or Both")
        else:
            result = self.merge_video_audio(video_type, audio_type)
            if result != -1:
                try:
                    os.remove(str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_video_dl" + str(video_type))
                    print("Removed Video")
                except:
                    print("Could not Remove Source Video")
                try:
                    os.remove(str(self.CHANNEL_SAVE_PATH) + "/" + str(self.title_clean) + "_audio_dl" + str(audio_type))
                    print("Removed Audio")
                except:
                    print("Could not Remove Source Audio")
            else:
                print("Could not Merge Two Source Files with FFMpeg")
        print('Video Downloaded: ', self.yt.title)
'''
