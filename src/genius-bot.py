#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from tkinter.filedialog import askopenfilename, askdirectory
import threading
import tkinter as tk
from tkinter import ttk, filedialog, font

import tkthread as tkt  # TkThread

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from youtube_download import YouTubeDownloader
from webpage_archive import WebPageArchive
from twitter_archive import TwitterDownloader
from report_merger import ReportMerge
from analytic_profiler import ReportAnalyzer
from log import Log
from version_info import geniusbot_version

# Implement the default Matplotlib key bindings.
'''from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure'''
import re
import os
import pyglet
import math
from PIL import ImageTk, Image

# Trade BOT Addition: https://blog.usejournal.com/a-step-by-step-guide-to-building-a-trading-bot-in-any-programming-language-d202ffe91569

# GeniusBot Classs
class GeniusBot:
    version = geniusbot_version
    tkt = None
    root = None
    log = None
    status = None
    tabControl = None
    style = None
    font = None
    hex_color_background = '#3E4A57'
    save_location = os.getcwd()
    title = None
    title_version = None
    home_title = None

    def __init__(self, root_main, tkt_main):
        self.log = Log()
        self.log.init_logging()
        # Always uncomment these logs for a build.
        # self.log.log_stdout()
        # self.log.log_stderr()
        self.root = root_main
        self.root.minsize(width=500, height=700)
        self.root.title(f"GeniusBot")
        self.root.geometry("600x700")
        self.tkt = tkt_main
        self.init_font()
        self.init_icon()
        self.title = tk.StringVar()
        self.title_version = tk.StringVar()
        self.home_title = tk.StringVar()
        self.init_styles()
        self.init_main_frame()
        self.log.info("Initializing GeniusBot Complete!")

    def init_font(self):
        font_path = f'{os.pardir}/fonts/OpenSans/OpenSans-Regular.ttf'
        font_path_alt = f'{os.curdir}/fonts/OpenSans/OpenSans-Regular.ttf'
        if os.path.isfile(font_path):
            pyglet.font.add_file(font_path)
            pyglet.font.load('OpenSans')
            self.font = tk.font.Font(family="OpenSans", size=10)
            # self.font = tk.font.Font(family="Times New Roman", size=12)
            print("Using Open_Sans")
        elif os.path.isfile(font_path_alt):
            pyglet.font.add_file(font_path_alt)
            # action_man = pyglet.font.load('OpenSans')
            pyglet.font.load('OpenSans')
            self.font = tk.font.Font(family="OpenSans", size=10)
            # self.font = tk.font.Font(family="Times New Roman", size=12)
            print("Using Open_Sans")
        else:
            print("Using Times new Roman")
            self.font = tk.font.Font(family="Times New Roman", size=10)

    def init_icon(self):
        icon_path = f'{os.pardir}/img/geniusbot.ico'
        if os.path.isfile(icon_path):
            print("Icon Found")
        else:
            icon_path = f'{os.curdir}/img/geniusbot.ico'
        print(icon_path)
        try:
            self.root.iconbitmap(os.path.abspath(icon_path))
        except tk.TclError:
            print("Icon not found")
            try:
                self.root.wm_iconbitmap(os.path.abspath(icon_path))
            except tk.TclError:
                print("Icon not found")

    def init_styles(self):
        self.style = ttk.Style()
        self.style.theme_create("GeniusBot", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [1, 5, 1, 0]}, "background": "white"},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": "black"},
                "map": {"background": [("selected", "black")],
                        "expand": [("selected", [1, 1, 1, 0])]}}})
        self.style.configure("TFrame", forground="black", font=self.font, background=self.hex_color_background)
        self.style.configure("TButton", foreground="#081e2a", font=self.font, background=self.hex_color_background)
        self.style.configure("TCheckbutton", font=self.font, background=self.hex_color_background, anchor="center",
                             foreground="white")
        self.style.configure("Add.TButton", foreground="green", font=self.font, background="green")
        self.style.configure("Open.TButton", foreground="orange", font=self.font, background="orange")
        self.style.configure("Remove.TButton", foreground="red", font=self.font, background="red")
        self.style.configure("TLabel", foreground="black", font=self.font, background=self.hex_color_background)
        self.style.configure("Status.TLabel", foreground="white", font=self.font, background=self.hex_color_background)
        self.style.configure("Title.TLabel", foreground="white", background=self.hex_color_background,
                             font=("OpenSans", 21), anchor="center")
        self.style.configure("SecondTitle.TLabel", font=tk.font.Font(family="OpenSans", size=14), anchor="center",
                             foreground="white")
        self.style.configure("Version.TLabel", font=tk.font.Font(family="OpenSans", size=14), anchor="center",
                             foreground="#0099d8")
        self.style.configure('.', font=self.font, foreground="white")
        self.style.configure("Notes.TLabel", font=self.font, anchor="center", foreground="white")
        self.style.configure("TMenubutton", font=self.font, anchor="center", foreground="black")
        self.style.configure("File.TLabel", background=self.hex_color_background, foreground="white", font=self.font,
                             borderwidth=5, relief="ridge")
        self.style.configure("Top.TFrame", background=self.hex_color_background, font=self.font)
        self.style.configure("TNotebook", font=self.font, background=self.hex_color_background, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=self.font, background=self.hex_color_background, foreground="black",
                             lightcolor="grey", borderwidth=2)

    def init_main_frame(self):
        # Main Frame UI
        tk.Grid.rowconfigure(self.root, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.root, 0, minsize=1, weight=1)
        main_frame = ttk.Frame(self.root)
        tk.Grid.rowconfigure(main_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(main_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(main_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(main_frame, 0, minsize=1, weight=1)
        main_frame.grid(row=0, column=0, sticky='NSEW')

        self.title.set(f"GeniusBot")
        self.title_version.set(f"v{geniusbot_version}")
        title_frame = ttk.Frame(main_frame)
        tk.Grid.rowconfigure(title_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(title_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(title_frame, 1, minsize=1, weight=1)
        title_label = ttk.Label(title_frame, textvariable=self.title, style="Title.TLabel")
        title_version_label = ttk.Label(title_frame, textvariable=self.title_version, style="Notes.TLabel")
        self.tabControl = ttk.Notebook(main_frame)
        notification_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky='NSEW')
        notification_frame.grid(row=5, column=0, sticky='NSEW')
        title_label.grid(column=0, row=0, sticky='NSE', columnspan=1, padx=(10, 5), pady=10)
        title_version_label.grid(column=1, row=0, sticky='NSW', columnspan=1, padx=(0, 10), pady=(20, 10))
        # Sets up Status Bar
        self.status = tk.StringVar()
        self.status.set(f"Welcome {os.getlogin()}! Please navigate to a tab to begin using GeniusBot!")
        status_label = tk.Label(notification_frame, bg=self.hex_color_background, fg="white", bd=1,
                                textvariable=self.status, anchor='w', relief=tk.SUNKEN)
        status_label.grid(column=0, row=0, sticky='NSEW', columnspan=1)
        self.init_home_frame()
        YouTubeFrame(self.tkt, self.tabControl, self.status, self.log)
        WebArchiveFrame(self.tkt, self.tabControl, self.status, self.log)
        TwitterArchiveFrame(self.tkt, self.tabControl, self.status, self.log)
        ReportMergeFrame(self.tkt, self.tabControl, self.status, self.log)
        AnalyticalProfilerFrame(self.tkt, self.tabControl, self.status, self.log)
        MediaConverterFrame(self.tkt, self.tabControl, self.status, self.log)
        self.tabControl.grid(column=0, row=1, sticky='NSEW')

    def init_home_frame(self):
        home_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(home_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(home_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(home_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(home_frame, 0, minsize=1, weight=1)
        top_frame_home = ttk.Frame(home_frame)
        tk.Grid.rowconfigure(top_frame_home, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_frame_home, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_frame_home, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_frame_home, 0, minsize=1, weight=1)

        self.home_title.set(
            f"""GeniusBot is a world class tool that allows you to do a lot of useful\n
            things from a compact and portable application\n
            1. YouTube Archive\n
            2. Web Archive\n            
            3. Analytical Profiler (Coming Soon)\n
            4. Report Merger (Coming Soon)\n
            5. FFMPEG Video/Audio Converter (Coming Soon)\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
            """)
        home_title_label = ttk.Label(top_frame_home, textvariable=self.home_title, anchor='w', style="Notes"
                                                                                                     ".TLabel")
        top_frame_home.grid(row=1, column=0, sticky='NSEW')
        home_title_label.grid(column=0, row=0, columnspan=3)
        self.tabControl.add(home_frame, text="Home")


# YouTubeArchive Class
class YouTubeFrame(tk.Frame):
    progress_bar_youtube = None
    progress_bar_value_youtube = 0
    progress_bar_max_value_youtube = 0
    url_list_youtube = []
    youtube_downloader = None
    log = None
    tabControl = None
    youtube_archive_frame = None
    status = None
    add_url_button = None
    remove_url_button = None
    openfile_button = None
    save_location = None
    save_location_button = None
    file_type = None
    file_type_menu = None
    video_quality_type = None
    video_quality_type_menu = None
    audio_quality_type = None
    audio_quality_type_menu = None
    download_button = None
    queue_title = None
    queue_title_label = None
    youtube_links_text = None
    youtube_links_label = None
    youtube_channels_text = None
    youtube_channels_label = None
    youtube_percentage_text = None
    percentage_label = None
    percentage_title = None
    percentage_title_label = None
    url_listbox = None
    url_entry = None
    channel_entry = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        # self.web_archive_frame = web_archive_frame
        self.youtube_downloader = YouTubeDownloader(self.log)
        self.draw_frame()
        self.tabControl.add(self.youtube_archive_frame, text="YouTube Archive")
        tk.Frame.__init__(self, self.youtube_archive_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    def draw_frame(self):
        self.youtube_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.youtube_archive_frame, 0, minsize=1, weight=1)
        top_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(top_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_frame, 0, minsize=1, weight=1)
        middle_button_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(middle_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(middle_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_button_frame, 3, minsize=1, weight=1)
        middle_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(middle_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_frame, 0, minsize=1, weight=1)
        bottom_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(bottom_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(bottom_frame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(bottom_frame, 2, minsize=1, weight=1)

        # Buttons
        self.add_url_button = ttk.Button(middle_button_frame, text="Add", style='Add.TButton', width=12,
                                         command=self.add_youtube_url)
        self.add_url_button.grid(column=0, row=1, sticky='NSEW', padx=5, pady=10)
        self.remove_url_button = ttk.Button(middle_button_frame, text="Remove", style='Remove.TButton', width=12,
                                            command=self.remove_youtube_url)
        self.remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=5, pady=10)
        self.openfile_button = ttk.Button(middle_button_frame, text="Open File", style='Open.TButton', width=12,
                                          command=self.open_file_youtube)
        self.openfile_button.grid(column=2, row=1, sticky='NSEW', padx=5, pady=10)
        self.save_location_button = ttk.Button(middle_button_frame, text="Save Location", width=18,
                                               command=self.choose_save_location_youtube)

        self.save_location_button.grid(column=3, row=1, sticky='NSEW', padx=5, pady=10)

        self.file_type = tk.StringVar()
        self.file_type.set("Video")
        self.file_type_menu = tk.OptionMenu(bottom_frame, self.file_type, "Video", "Audio",
                                            command=self.set_file_type)
        self.video_quality_type = tk.StringVar()
        self.video_quality_type.set("Highest")
        self.video_quality_type_menu = tk.OptionMenu(bottom_frame, self.video_quality_type, "Highest", "720p",
                                                     "Lowest")
        self.audio_quality_type = tk.StringVar()
        self.audio_quality_type.set("320kbps")
        self.audio_quality_type_menu = tk.OptionMenu(bottom_frame, self.audio_quality_type, "320kbps", "256kbps",
                                                     "128kbps")

        self.file_type_menu.grid(column=0, row=3, sticky='NSEW', padx=5, pady=10)
        self.video_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
        # self.audio_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
        # self.audio_quality_type_menu.grid_forget()
        self.download_button = ttk.Button(bottom_frame, text="Download",
                                          command=lambda: self.run(lambda: self.youtube_download(), name='NoSync'))
        self.download_button.grid(column=2, row=3, sticky='NSEW', padx=15, pady=10)
        # Labels
        self.queue_title = tk.StringVar()
        self.queue_title.set("Download Queue")
        self.queue_title_label = ttk.Label(middle_frame, textvariable=self.queue_title, style="Notes.TLabel")
        self.queue_title_label.grid(column=0, row=0, columnspan=3)
        self.youtube_links_text = tk.StringVar()
        self.youtube_links_text.set(r'Enter YouTube Link(s) ⮟')
        self.youtube_links_label = ttk.Label(top_frame, textvariable=self.youtube_links_text,
                                             style="Notes.TLabel")
        self.youtube_links_label.grid(column=0, row=0, columnspan=2, sticky='W')
        self.youtube_channels_text = tk.StringVar()
        self.youtube_channels_text.set(r'Enter YouTube Channel or User ⮞')
        self.youtube_channels_label = ttk.Label(top_frame, textvariable=self.youtube_channels_text,
                                                style="Notes.TLabel")
        self.youtube_channels_label.grid(column=0, row=4, columnspan=2, sticky='W')
        self.youtube_percentage_text = tk.StringVar()
        self.youtube_percentage_text.set((
            f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
            f"{(self.progress_bar_value_youtube / (self.progress_bar_max_value_youtube + 1)) * 100}%"))
        self.percentage_label = ttk.Label(bottom_frame, textvariable=self.youtube_percentage_text,
                                          style="Notes.TLabel")
        self.percentage_label.grid(column=0, row=2, columnspan=3)
        self.percentage_title = tk.StringVar()
        self.percentage_title.set("Percentage")
        self.percentage_title_label = ttk.Label(bottom_frame, textvariable=self.percentage_title,
                                                style="Notes.TLabel")
        self.percentage_title_label.grid(column=0, row=0, columnspan=3)

        # ListBox
        self.url_listbox = tk.Listbox(middle_frame, height=12, selectmode='multiple', exportselection=0)
        self.url_listbox.grid(column=0, row=1, columnspan=3, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.url_listbox, 0, weight=1)

        # Entries
        self.url_entry = tk.Text(top_frame, height=9)
        self.channel_entry = tk.Text(top_frame, height=1, width=33)
        # tk.Grid.columnconfigure(self.url_entry, 0, weight=1)
        self.channel_entry.bind("<Tab>", self.focus_next_widget)
        self.channel_entry.grid(column=1, row=4, columnspan=2, stick='NSEW')
        self.url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_youtube_list()
        self.url_entry.grid(column=0, row=2, columnspan=3, sticky='NSEW')

        # Progress Bar
        self.progress_bar_youtube = ttk.Progressbar(
            bottom_frame, orient="horizontal",
            length=300, mode="determinate"
        )
        self.progress_bar_youtube.grid(column=0, row=1, padx=15, pady=10, columnspan=3, sticky='NSEW')
        top_frame.grid(row=1, column=0, sticky='NSEW')
        middle_button_frame.grid(row=2, column=0, sticky='NSEW')
        middle_frame.grid(row=3, column=0, sticky='NSEW')
        bottom_frame.grid(row=4, column=0, sticky='NSEW')

    def youtube_download(self):
        if self.file_type.get() == "Video":
            self.download_video(quality=self.video_quality_type.get())
        elif self.file_type.get() == "Audio":
            audio_quality = self.audio_quality_type.get()
            audio_quality = re.sub("[^0-9]", "", audio_quality)
            print("Audio Quality: ", audio_quality)
            self.download_audio(quality=audio_quality)

    def set_file_type(self, value):
        if self.file_type.get() == "Video":
            self.audio_quality_type_menu.grid_forget()
            self.video_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
            print(value)
        elif self.file_type.get() == "Audio":
            self.video_quality_type_menu.grid_forget()
            self.audio_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
            print(value)

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    def choose_save_location_youtube(self):
        self.save_location = tk.filedialog.askdirectory()
        print("Save Filepath: ", self.save_location)
        self.youtube_downloader.set_save_path(self.save_location)

    def open_file_youtube(self):
        name = tk.filedialog.askopenfilename(initialdir=os.getcwd(),
                                             filetypes=(("Text File", "*.txt"), ("All Files", "*.*")),
                                             title="Choose a file."
                                             )
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            youtube_urls = open(name, 'r')
            print("youtube_urls", youtube_urls)
            print("Length of Links Before Open File: ", len(self.url_list_youtube))
            for url in youtube_urls:
                self.url_list_youtube.append(url)
            self.refresh_youtube_list()
            self.progress_bar_max_value_youtube = len(self.url_list_youtube)
            self.youtube_percentage_text.set((
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                f"{(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos from file: {name}')
        except Exception as e:
            print("No file exists: ", e)
            self.status.set(f'File Not Found')

    def refresh_youtube_list(self):
        self.url_listbox.delete(0, tk.END)
        self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
        for items in self.url_list_youtube:
            self.url_listbox.insert(tk.END, items)

    def add_youtube_url(self):
        # Get Channel
        parse_channel_addition = self.channel_entry.get("1.0", tk.END)
        print("Parsed Addition: ", parse_channel_addition)
        if re.sub(r'[^A-Za-z0-9_./:&-?!=]', '', parse_channel_addition) != "":
            parse_channel_addition = parse_channel_addition.rstrip()
            self.youtube_downloader.get_channel_videos(parse_channel_addition)
            parse_addition_array = self.youtube_downloader.get_link()
            self.youtube_downloader.reset_links()
            for url in parse_addition_array:
                if re.sub(r'[^A-Za-z0-9_./:&-?!=]', '', url) != "":
                    self.status.set(f'Added URLs to Queue')
                    temp = re.sub(r'[^A-Za-z0-9_./:&-?!=]', '', url)
                    print("Appended: ", temp)
                    self.url_list_youtube.append(temp)
                else:
                    print("Bad URL: ", url)
                    self.status.set(f'Paste Some YouTube Links First! (CTRL+V) {url}')
            self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
            self.channel_entry.delete("1.0", tk.END)
            self.refresh_youtube_list()
            self.progress_bar_max_value_youtube = len(self.url_list_youtube)
            self.youtube_percentage_text.set((
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                f"{(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos')
        # Get Videos
        parse_addition = self.url_entry.get("1.0", tk.END)
        if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', parse_addition) != "":
            parse_addition_array = parse_addition.splitlines()
            for url in parse_addition_array:
                if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url) != "":
                    self.status.set(f'Added URLs to Queue')
                    temp = re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url)
                    self.url_list_youtube.append(temp)
                else:
                    print("Bad URL: ", url)
                    self.status.set(f'Paste Some YouTube Links First! (CTRL+V) {url}')
            self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
            self.url_entry.delete("1.0", tk.END)
            self.refresh_youtube_list()
            self.progress_bar_max_value_youtube = len(self.url_list_youtube)
            self.youtube_percentage_text.set((
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                f"{(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos')

    def remove_youtube_url(self):
        if self.url_listbox.curselection():
            selected_text_list = [self.url_listbox.get(i) for i in self.url_listbox.curselection()]
            x = 0
            for url in selected_text_list:
                self.url_list_youtube.remove(url)
                x += 1
            self.refresh_youtube_list()
            self.progress_bar_max_value_youtube = len(self.url_list_youtube)
            if self.progress_bar_max_value_youtube == 0:
                self.youtube_percentage_text.set(
                    f"{self.progress_bar_max_value_youtube}/{self.progress_bar_max_value_youtube} | {0 * 100}%")
                self.progress_bar_youtube['value'] = 0
                self.progress_bar_value_youtube = 0
            else:
                self.youtube_percentage_text.set((
                    f"{self.progress_bar_max_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                    f"{(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%"))
                self.progress_bar_youtube['value'] = self.progress_bar_value_youtube
                self.progress_bar_youtube['maximum'] = self.progress_bar_max_value_youtube
                self.progress_bar_value_youtube = self.progress_bar_max_value_youtube
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos')
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    def download_video(self, quality):
        self.url_list_youtube = list(filter(None, self.url_list_youtube))
        self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
        self.progress_bar_max_value_youtube = len(self.url_list_youtube)
        if self.progress_bar_max_value_youtube > 0:
            self.status.set(f'Downloading {len(self.url_list_youtube)} URL(s)')
            # self.tabControl.tab(2, state="disabled")
            # self.tabControl.tab(3, state="disabled")
            self.download_button["state"] = "disabled"
            self.add_url_button["state"] = "disabled"
            self.remove_url_button["state"] = "disabled"
            self.openfile_button["state"] = "disabled"
            self.save_location_button["state"] = "disabled"
            self.progress_bar_value_youtube = 0
            self.progress_bar_youtube['maximum'] = self.progress_bar_max_value_youtube
            self.progress_bar_youtube['value'] = 0
            self.youtube_percentage_text.set((
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                f"{math.ceil((self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100)}%"))
            i = 0
            for url in self.url_list_youtube:
                self.youtube_downloader.append_link(url)
                print("Links Sent: ", self.youtube_downloader.get_link())
                self.youtube_downloader.download_videos(quality)
                self.youtube_downloader.reset_links()
                self.progress_bar_value_youtube = i + 1
                self.youtube_percentage_text.set((
                    f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                    f"{math.ceil((self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100)}%"))
                self.progress_bar_youtube['value'] = i + 1
                print("Value: ", self.progress_bar_value_youtube)
                print("Max Value: ", self.progress_bar_max_value_youtube)
                self.status.set(f'Completed {self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube}')
                i += 1
            self.tabControl.tab(1, state="normal")
            self.tabControl.tab(2, state="normal")
            self.download_button["state"] = "enabled"
            self.add_url_button["state"] = "enabled"
            self.remove_url_button["state"] = "enabled"
            self.openfile_button["state"] = "enabled"
            self.save_location_button["state"] = "enabled"
            self.status.set(f'Downloaded {self.progress_bar_value_youtube} video(s)!')
        else:
            print("No Videos Added")
            self.status.set(f'Add Some Videos First!')

    def download_audio(self, quality):
        self.url_list_youtube = list(filter(None, self.url_list_youtube))
        self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
        self.progress_bar_max_value_youtube = len(self.url_list_youtube)
        if self.progress_bar_max_value_youtube > 0:
            self.status.set(f'Downloading {len(self.url_list_youtube)} URL(s)')
            self.download_button["state"] = "disabled"
            self.add_url_button["state"] = "disabled"
            self.remove_url_button["state"] = "disabled"
            self.openfile_button["state"] = "disabled"
            self.save_location_button["state"] = "disabled"
            self.progress_bar_value_youtube = 0
            self.progress_bar_youtube['maximum'] = self.progress_bar_max_value_youtube
            self.progress_bar_youtube['value'] = 0
            self.youtube_percentage_text.set((
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                f"{math.ceil((self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100)}%"))
            i = 0
            for url in self.url_list_youtube:
                self.youtube_downloader.append_link(url)
                self.youtube_downloader.download_audio(quality=quality)
                self.youtube_downloader.reset_links()
                self.progress_bar_value_youtube = i + 1
                self.youtube_percentage_text.set((
                    f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | ",
                    f"{math.ceil((self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100)}%"))
                self.progress_bar_youtube['value'] = i + 1
                print("Value: ", self.progress_bar_value_youtube)
                print("Max Value: ", self.progress_bar_max_value_youtube)
                self.status.set(f'Completed {self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube}')
                i += 1
            self.download_button["state"] = "enabled"
            self.add_url_button["state"] = "enabled"
            self.remove_url_button["state"] = "enabled"
            self.openfile_button["state"] = "enabled"
            self.save_location_button["state"] = "enabled"
            self.status.set(f'Downloaded {self.progress_bar_value_youtube} audio!')
        else:
            print("No Videos Added")
            self.status.set(f'Add Some Videos First!')


# WebArchive Class
class WebArchiveFrame(tk.Frame):
    progress_bar_web_archive = None
    progress_bar_value_web_archive = 0
    progress_bar_max_value_web_archive = 0
    url_list_web_archive = []
    web_archive = None
    log = None
    tabControl = None
    web_archive_frame = None
    status = None
    save_location = None
    web_add_url_button = None
    web_remove_url_button = None
    web_openfile_button = None
    web_save_location_button = None
    web_archive_button = None
    web_queue_title = None
    web_queue_title_label = None
    web_config_title = None
    web_config_title_label = None
    web_config_screenshot_value = None
    web_config_screenshot = None
    web_screenshot_filetype_title = None
    web_screenshot_filetype = None
    web_screenshot_filetype_menu = None
    web_screenshot_size_title = None
    web_screenshot_size = None
    web_screenshot_size_menu = None
    web_screenshot_quality_title = None
    web_screenshot_quality_value = None
    web_screenshot_quality = None
    web_zoom_title = None
    web_zoom_value = None
    web_zoom = None
    web_config_html_dl_value = None
    web_config_html_dl = None
    web_config_compress_value = None
    web_config_compress = None
    web_config_twitter_value = None
    web_config_twitter = None
    web_links_text = None
    web_links_label = None
    web_url_listbox = None
    web_url_entry = None
    web_percentage_text = None
    web_percentage_title = None
    web_percentage_label = None
    web_percentage_title_label = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        self.web_archive = WebPageArchive(self.log)
        self.draw_frame()
        self.tabControl.add(self.web_archive_frame, text="Web Archive")
        tk.Frame.__init__(self, self.web_archive_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    def draw_frame(self):
        self.web_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.web_archive_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.web_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.web_archive_frame, 1, minsize=1, weight=1)
        web_archive_selection_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(web_archive_selection_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(web_archive_selection_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(web_archive_selection_frame, 0, minsize=1, weight=1)
        web_archive_config_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(web_archive_config_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(web_archive_config_frame, 0, minsize=1, weight=0)
        top_web_frame = ttk.Frame(web_archive_selection_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(top_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_web_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_web_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_web_frame, 0, minsize=1, weight=1)
        middle_web_button_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(middle_web_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(middle_web_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 3, minsize=1, weight=1)
        middle_web_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(middle_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_web_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_frame, 0, minsize=1, weight=1)
        bottom_web_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_web_frame, 1, minsize=1, weight=1)

        # tk.Grid.rowconfigure(self.notification_frame, 0, minsize=1, weight=1)
        # tk.Grid.columnconfigure(self.notification_frame, 0, minsize=1, weight=1)
        # Buttons
        self.web_add_url_button = ttk.Button(middle_web_button_frame, text="Add", style='Add.TButton', width=9,
                                             command=self.add_webarchive_url)
        self.web_add_url_button.grid(column=0, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_remove_url_button = ttk.Button(middle_web_button_frame, text="Remove", style='Remove.TButton',
                                                width=9, command=self.remove_webarchive_url)
        self.web_remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_openfile_button = ttk.Button(middle_web_button_frame, text="Open File", style='Open.TButton',
                                              width=9, command=self.open_file_webarchive)
        self.web_openfile_button.grid(column=2, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_save_location_button = ttk.Button(middle_web_button_frame, text="Save Location", width=15,
                                                   command=self.choose_save_location_webarchive)
        self.web_save_location_button.grid(column=3, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_archive_button = ttk.Button(bottom_web_frame, text="Begin Archive",
                                             command=lambda: self.run(lambda: self.archive_sites(), name='NoSync'))
        self.web_archive_button.grid(column=0, row=3, columnspan=2, sticky='NSEW', padx=15, pady=10)

        # Labels
        # self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.web_queue_title = tk.StringVar()
        self.web_queue_title.set("Download Queue")
        self.web_queue_title_label = ttk.Label(middle_web_frame,
                                               textvariable=self.web_queue_title,
                                               style="Notes.TLabel")
        self.web_queue_title_label.grid(column=0, row=0, columnspan=1)
        self.web_config_title = tk.StringVar()
        self.web_config_title.set("Configure Archive")
        self.web_config_title_label = ttk.Label(web_archive_config_frame, textvariable=self.web_config_title,
                                                style="Notes.TLabel")
        self.web_config_title_label.grid(column=0, row=0, columnspan=2, pady=(5, 5), sticky='NSEW')
        self.web_config_screenshot_value = tk.IntVar()
        self.web_config_screenshot_value.set(1)
        self.web_config_screenshot = ttk.Checkbutton(web_archive_config_frame, text="Capture Screenshot",
                                                     variable=self.web_config_screenshot_value, onvalue=1, offvalue=0,
                                                     style="TCheckbutton", command=self.onclick_capture_screenshot)
        self.web_config_screenshot.grid(column=0, row=1, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_filetype_title = ttk.Label(web_archive_config_frame, text="File Type",
                                                       style="Notes.TLabel")
        self.web_screenshot_filetype_title.grid(column=0, row=2, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_filetype = tk.StringVar()
        self.web_screenshot_filetype.set("PNG")  # default value
        self.web_screenshot_filetype_menu = ttk.OptionMenu(web_archive_config_frame, self.web_screenshot_filetype,
                                                           "PNG", "PNG", "JPEG")
        self.web_screenshot_filetype_menu.grid(column=1, row=2, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_size_title = ttk.Label(web_archive_config_frame, text="Size",
                                                   style="Notes.TLabel")
        self.web_screenshot_size_title.grid(column=0, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_size = tk.StringVar()
        self.web_screenshot_size.set("Full")  # default value
        self.web_screenshot_size_menu = ttk.OptionMenu(web_archive_config_frame, self.web_screenshot_size,
                                                       "Full", "Full", "Normal")
        self.web_screenshot_size_menu.grid(column=1, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_quality_title = ttk.Label(web_archive_config_frame, text="Quality",
                                                      style="Notes.TLabel")
        self.web_screenshot_quality_title.grid(column=0, row=4, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_quality_value = tk.IntVar()
        self.web_screenshot_quality_value.set(100)
        self.web_screenshot_quality = tk.Scale(web_archive_config_frame, from_=10, to=100,
                                               variable=self.web_screenshot_quality_value, orient=tk.HORIZONTAL)
        self.web_screenshot_quality.grid(column=1, row=4, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_zoom_title = ttk.Label(web_archive_config_frame, text="Zoom %", style="Notes.TLabel")
        self.web_zoom_title.grid(column=0, row=5, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_zoom_value = tk.IntVar()
        self.web_zoom_value.set(100)
        self.web_zoom = tk.Scale(web_archive_config_frame, from_=25, to=500,
                                 variable=self.web_zoom_value, command=self.zoom_increment_value, orient=tk.HORIZONTAL)
        self.web_zoom.grid(column=1, row=5, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_html_dl_value = tk.IntVar()
        self.web_config_html_dl = ttk.Checkbutton(web_archive_config_frame, text="Archive Website",
                                                  variable=self.web_config_html_dl_value, onvalue=1, offvalue=0,
                                                  style="TCheckbutton")
        self.web_config_html_dl.grid(column=0, row=6, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_compress_value = tk.IntVar()
        self.web_config_compress = ttk.Checkbutton(web_archive_config_frame, text="Compress/Zip",
                                                   variable=self.web_config_compress_value, onvalue=1, offvalue=0,
                                                   style="TCheckbutton")
        self.web_config_compress.grid(column=0, row=7, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_twitter_value = tk.IntVar()
        self.web_config_twitter = ttk.Checkbutton(web_archive_config_frame, text="Twitter to CSV",
                                                  variable=self.web_config_twitter_value, onvalue=1, offvalue=0,
                                                  style="TCheckbutton")
        self.web_config_twitter.grid(column=0, row=8, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_links_text = tk.StringVar()
        self.web_links_text.set(r'Enter Web Link(s) ⮟')
        self.web_links_label = ttk.Label(top_web_frame, textvariable=self.web_links_text, style="Notes.TLabel")
        self.web_links_label.grid(column=0, row=0, columnspan=1, sticky='W')
        self.web_percentage_text = tk.StringVar()
        self.web_percentage_text.set((
            f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
            f"{(self.progress_bar_value_web_archive / (self.progress_bar_max_value_web_archive + 1)) * 100}%"))
        self.web_percentage_label = ttk.Label(bottom_web_frame, textvariable=self.web_percentage_text,
                                              style="Notes.TLabel")
        self.web_percentage_label.grid(column=0, row=2, columnspan=2)
        self.web_percentage_title = tk.StringVar()
        self.web_percentage_title.set("Percentage")
        self.web_percentage_title_label = ttk.Label(bottom_web_frame, textvariable=self.web_percentage_title,
                                                    style="Notes.TLabel")
        self.web_percentage_title_label.grid(column=0, row=0, columnspan=2)

        # ListBox
        self.web_url_listbox = tk.Listbox(middle_web_frame, height=12, selectmode='multiple', exportselection=0)
        self.web_url_listbox.grid(column=0, row=1, columnspan=2, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.web_url_listbox, 0, weight=1)

        # Entries
        self.web_url_entry = tk.Text(top_web_frame, height=9)
        self.web_url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_webarchive_list()
        self.web_url_entry.grid(column=0, row=2, columnspan=2, sticky='NSEW')

        # Progress Bar
        self.progress_bar_web_archive = ttk.Progressbar(
            bottom_web_frame, orient="horizontal",
            mode="determinate"
        )
        web_archive_selection_frame.grid(column=1, row=0, columnspan=1, sticky='NSEW')
        web_archive_config_frame.grid(column=0, row=0, columnspan=1, sticky='NSEW')
        self.progress_bar_web_archive.grid(column=0, row=1, padx=15, pady=10, columnspan=2, sticky='NSEW')
        top_web_frame.grid(row=1, column=0, sticky='NSEW')
        middle_web_button_frame.grid(row=2, column=0, sticky='NSEW')
        middle_web_frame.grid(row=3, column=0, sticky='NSEW')
        bottom_web_frame.grid(row=4, column=0, sticky='NSEW')

    def zoom_increment_value(self, value):
        value_list = [25, 33, 50, 67, 75, 80, 90, 100, 110, 125, 150, 175, 200, 250, 300, 400, 500]
        new_value = min(value_list, key=lambda x: abs(x - float(value)))
        self.web_zoom.set(new_value)

    def archive_sites(self):
        self.url_list_web_archive = list(filter(None, self.url_list_web_archive))
        self.url_list_web_archive = list(dict.fromkeys(self.url_list_web_archive))
        self.progress_bar_max_value_web_archive = len(self.url_list_web_archive)
        if self.progress_bar_max_value_web_archive > 0:
            self.status.set(f'Downloading {len(self.url_list_web_archive)} URL(s)')
            self.web_archive_button["state"] = "disabled"
            self.web_add_url_button["state"] = "disabled"
            self.web_remove_url_button["state"] = "disabled"
            self.web_openfile_button["state"] = "disabled"
            self.web_save_location_button["state"] = "disabled"
            self.progress_bar_value_web_archive = 0
            self.progress_bar_web_archive['maximum'] = self.progress_bar_max_value_web_archive
            self.progress_bar_web_archive['value'] = 0
            print(f'{self.progress_bar_max_value_web_archive}:MAX VALUE')
            self.web_percentage_text.set((
                f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
                f"{math.ceil((self.progress_bar_value_web_archive / self.progress_bar_max_value_web_archive) * 100)}%"))
            # Check to see if screenshot capture is enabled to launch browser
            if self.web_config_screenshot_value.get() == 1:
                self.web_archive.launch_browser(len(self.url_list_web_archive))
            i = 0
            for url in self.url_list_web_archive:
                self.web_archive.append_link(url=url)
                print("Links Sent: ", self.web_archive.get_links())
                # Check to see if screenshot capture is enabled to capture screenshot
                if self.web_config_screenshot_value.get() == 1:
                    if self.web_screenshot_size.get() == "Full":
                        self.web_archive.fullpage_screenshot(url=url,
                                                             zoom_percentage=self.web_zoom_value.get(),
                                                             filetype=self.web_screenshot_filetype.get(),
                                                             quality=self.web_screenshot_quality.get())
                    elif self.web_screenshot_size.get() == "Normal":
                        self.web_archive.screenshot(url=url,
                                                    zoom_percentage=self.web_zoom_value.get(),
                                                    filetype=self.web_screenshot_filetype.get(),
                                                    quality=self.web_screenshot_quality.get())
                self.web_archive.reset_links()
                self.progress_bar_value_web_archive = i + 1
                self.web_percentage_text.set((
                    f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
                    f"{math.ceil((self.progress_bar_value_web_archive / self.progress_bar_max_value_web_archive) * 100)}",
                    f"%"))
                self.progress_bar_web_archive['value'] = i + 1
                print("Value: ", self.progress_bar_value_web_archive)
                print("Max Value: ", self.progress_bar_max_value_web_archive)
                self.status.set(
                    f'Completed {self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive}')
                i += 1
            # Check to see if screenshot capture is enabled to quit browser
            if self.web_config_screenshot_value.get() == 1:
                self.web_archive.quit_driver()
            self.tabControl.tab(1, state="normal")
            self.tabControl.tab(2, state="normal")
            self.web_archive_button["state"] = "enabled"
            self.web_add_url_button["state"] = "enabled"
            self.web_remove_url_button["state"] = "enabled"
            self.web_openfile_button["state"] = "enabled"
            self.web_save_location_button["state"] = "enabled"
            self.status.set(f'Downloaded {self.progress_bar_value_web_archive} website screenshot(s)!')
        else:
            print("No Website Links Added")
            self.status.set(f'Add Some Website Links First!')

    def onclick_capture_screenshot(self):
        value = self.web_config_screenshot_value.get()
        if value == 0:
            self.web_screenshot_filetype_title.grid_forget()
            self.web_screenshot_filetype_menu.grid_forget()
            self.web_screenshot_size_title.grid_forget()
            self.web_screenshot_size_menu.grid_forget()
            self.web_screenshot_quality_title.grid_forget()
            self.web_screenshot_quality.grid_forget()
        elif value == 1:
            self.web_screenshot_filetype_title.grid(column=0, row=2, columnspan=1, padx=(5, 0), pady=(5, 5),
                                                    sticky='NSEW')
            self.web_screenshot_filetype_menu.grid(column=1, row=2, columnspan=1, padx=(5, 5), pady=(5, 5),
                                                   sticky='NSEW')
            self.web_screenshot_size_title.grid(column=0, row=3, columnspan=1, padx=(5, 0), pady=(0, 5), sticky='NSEW')
            self.web_screenshot_size_menu.grid(column=1, row=3, columnspan=1, padx=(5, 5), pady=(0, 5), sticky='NSEW')
            self.web_screenshot_quality_title.grid(column=0, row=4, columnspan=1, padx=(5, 0), pady=(0, 5),
                                                   sticky='NSEW')
            self.web_screenshot_quality.grid(column=1, row=4, columnspan=1, padx=(5, 5), pady=(0, 5), sticky='NSEW')

    def choose_save_location_webarchive(self):
        self.save_location = tk.filedialog.askdirectory()
        print("Save Filepath: ", self.save_location)
        self.web_archive.set_save_path(self.save_location)

    def open_file_webarchive(self):
        name = tk.filedialog.askopenfilename(initialdir=os.getcwd(),
                                             filetypes=(("Text File", "*.txt"), ("All Files", "*.*")),
                                             title="Choose a file."
                                             )
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            webarchive_urls = open(name, 'r')
            print("webarchive_urls", webarchive_urls)
            print("Length of Links Before Open File: ", len(self.url_list_web_archive))
            for url in webarchive_urls:
                self.url_list_web_archive.append(url)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_web_archive = len(self.url_list_web_archive)
            self.web_percentage_text.set((
                f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
                f"{(self.progress_bar_value_web_archive / self.progress_bar_max_value_web_archive) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_web_archive} videos from file: {name}')
        except Exception as e:
            print("No file exists: ", e)
            self.status.set(f'File Not Found')

    def refresh_webarchive_list(self):
        self.web_url_listbox.delete(0, tk.END)
        self.url_list_web_archive = list(dict.fromkeys(self.url_list_web_archive))
        for items in self.url_list_web_archive:
            self.web_url_listbox.insert(tk.END, items)

    def add_webarchive_url(self):
        # Get Web Links
        parse_addition = self.web_url_entry.get("1.0", tk.END)
        if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', parse_addition) != "":
            parse_addition_array = parse_addition.splitlines()
            for url in parse_addition_array:
                if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url) != "":
                    self.status.set(f'Added URLs to Queue')
                    temp = re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url)
                    self.url_list_web_archive.append(temp)
                else:
                    print("Bad URL: ", url)
                    self.status.set(f'Paste Some Website Links First! (CTRL+V) {url}')
            self.url_list_web_archive = list(dict.fromkeys(self.url_list_web_archive))
            self.web_url_entry.delete("1.0", tk.END)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_web_archive = len(self.url_list_web_archive)
            print((
                f'URL: {self.url_list_web_archive} AND AND MAXVAL: {self.progress_bar_max_value_web_archive} AND LEN: '
                f' {len(self.url_list_web_archive)}'))
            self.web_percentage_text.set((
                f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
                f"{(self.progress_bar_value_web_archive / self.progress_bar_max_value_web_archive) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_web_archive} url(s)')

    def remove_webarchive_url(self):
        if self.web_url_listbox.curselection():
            selected_text_list = [self.web_url_listbox.get(i) for i in self.web_url_listbox.curselection()]
            x = 0
            for url in selected_text_list:
                self.url_list_web_archive.remove(url)
                x += 1
            self.refresh_webarchive_list()
            self.progress_bar_max_value_web_archive = len(self.url_list_web_archive)
            if self.progress_bar_max_value_web_archive == 0:
                self.web_percentage_text.set(
                    f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | {0 * 100}%")
                self.progress_bar_web_archive['value'] = 0
                self.progress_bar_value_web_archive = 0
            else:
                self.web_percentage_text.set((
                    f"{self.progress_bar_value_web_archive}/{self.progress_bar_max_value_web_archive} | ",
                    f"{(self.progress_bar_value_web_archive / self.progress_bar_max_value_web_archive) * 100}%"))
                self.progress_bar_web_archive['value'] = self.progress_bar_max_value_web_archive
                self.progress_bar_web_archive['maximum'] = self.progress_bar_max_value_web_archive
                self.progress_bar_value_web_archive = self.progress_bar_max_value_web_archive
            self.status.set(f'Queued {self.progress_bar_max_value_web_archive} videos')
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"


# Pandas Report Merge Class
class ReportMergeFrame(tk.Frame):
    report_merger = None
    log = None
    tabControl = None
    report_merge_frame = None
    status = None
    inner_join_tip = "Inner Join: Returns records that have matching values in both files"
    left_join_tip = "Left Join: Returns all records from the left table, and the matched records from the right file"
    right_join_tip = "Right Join: Returns all records from the right table, and the matched records from the left file"
    outer_join_tip = "Outer Join: Returns all records when there is a match in either left or right file"
    append_join_tip = "Append: For Files with the same columns, it appends all rows from File 2 & File 1"
    csv_flag_rm = 1
    dtypes_list_file1 = []
    dtypes_list_file2 = []
    report_dtypes_f1 = []
    column_order_list_f1 = []
    report_dtypes_f2 = []
    column_order_list_f2 = []
    joins_list = None
    save_location = os.getcwd()
    file1_title_columns_rm_frame = None
    file2_title_columns_rm_frame = None
    file1_filename = None
    filename_1_text = None
    filename_1_label = None
    file2_filename = None
    filename_2_text = None
    filename_2_label = None
    save_location_button = None
    save_file_name_widget = None
    save_file_name_label = None
    join_tip_text = None
    join_tip_label = None
    joins = None
    join_type_label = None
    join_type_inner_image_path = None
    join_type_left_image_path = None
    join_type_right_image_path = None
    join_type_outer_image_path = None
    join_type_append_image_path = None
    join_type_inner_image_widget = None
    join_type_left_image_widget = None
    join_type_right_image_widget = None
    join_type_outer_image_widget = None
    join_type_append_image_widget = None
    join_type_inner_image = None
    join_type_left_image = None
    join_type_right_image = None
    join_type_outer_image = None
    join_type_append_image = None
    join_type_inner_image_panel = None
    join_type_left_image_panel = None
    join_type_right_image_panel = None
    join_type_outer_image_panel = None
    join_type_append_image_panel = None
    export_option_rm = None
    export_type_rm = None
    run_merge = None
    file_1_browse_button = None
    file_2_browse_button = None
    file1_columns_text = None
    file1_columns_label = None
    file1_columns_label_type_title = None
    file2_columns_text = None
    file2_columns_label = None
    file2_columns_label_type_title = None
    file1_keys = None
    file2_keys = None
    file1_pk = None
    file2_pk = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        self.report_merger = ReportMerge(self.log)
        self.draw_frame()
        self.tabControl.add(self.report_merge_frame, text="Report Merger")
        tk.Frame.__init__(self, self.report_merge_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    def draw_frame(self):
        # Setting up Frames in Report Merger Tab
        self.report_merge_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.report_merge_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.report_merge_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.report_merge_frame, 2, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.report_merge_frame, 3, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.report_merge_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.report_merge_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.report_merge_frame, 0, minsize=1, weight=1)
        title_rm_frame = ttk.Frame(self.report_merge_frame, style="Top.TFrame")
        top_rm_frame = ttk.Frame(self.report_merge_frame)
        middle_rm_frame = ttk.Frame(self.report_merge_frame)
        file_columns_rm_frame = ttk.Frame(self.report_merge_frame)
        self.file1_title_columns_rm_frame = ttk.Frame(file_columns_rm_frame)
        file1columns_rm_frame = ttk.Frame(file_columns_rm_frame)
        self.file2_title_columns_rm_frame = ttk.Frame(file_columns_rm_frame)
        file2columns_rm_frame = ttk.Frame(file_columns_rm_frame)
        lower_middle_rm_frame = ttk.Frame(self.report_merge_frame)
        lower_rm_frame = ttk.Frame(self.report_merge_frame)
        lowest_rm_frame = ttk.Frame(self.report_merge_frame)
        tk.Grid.rowconfigure(title_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(title_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.rowconfigure(top_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_rm_frame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(top_rm_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(middle_rm_frame, 2, minsize=1, weight=1)
        tk.Grid.rowconfigure(middle_rm_frame, 3, minsize=1, weight=0)
        tk.Grid.columnconfigure(middle_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(file_columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(file_columns_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(file_columns_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.file1_title_columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.file1_title_columns_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.rowconfigure(file1columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(file1columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(file1columns_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(file1columns_rm_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.file2_title_columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.file2_title_columns_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.rowconfigure(file2columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(file2columns_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(file2columns_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(file2columns_rm_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(lower_middle_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(lower_middle_rm_frame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(lower_middle_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(lower_middle_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(lower_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(lower_rm_frame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(lower_rm_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(lower_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(lowest_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(lowest_rm_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(lowest_rm_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(lowest_rm_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(lowest_rm_frame, 3, minsize=1, weight=0)
        tk.Grid.columnconfigure(lowest_rm_frame, 4, minsize=1, weight=0)
        title_rm_frame.grid(column=0, row=0, sticky='NSEW')
        top_rm_frame.grid(column=0, row=1, sticky='NSEW')
        middle_rm_frame.grid(column=0, row=2, sticky='NSEW')
        file_columns_rm_frame.grid(column=0, row=3, sticky='NSEW')
        self.file1_title_columns_rm_frame.grid(column=0, row=0, sticky='NSEW')
        file1columns_rm_frame.grid(column=0, row=1, sticky='NSEW')
        self.file2_title_columns_rm_frame.grid(column=1, row=0, sticky='NSEW')
        file2columns_rm_frame.grid(column=1, row=1, sticky='NSEW')
        lower_middle_rm_frame.grid(column=0, row=4, sticky='NSEW')
        lower_rm_frame.grid(column=0, row=5, sticky='NSEW')
        lowest_rm_frame.grid(column=0, row=6, sticky='NSEW')

        # Set the Buttons for the Report Merger class
        self.file1_filename = "Choose First File to be Merged"
        self.filename_1_text = tk.StringVar()
        self.filename_1_text.set(self.file1_filename)
        self.filename_1_label = ttk.Label(top_rm_frame, style="File.TLabel", textvariable=self.filename_1_text)
        self.filename_1_label.grid(row=0, column=0, padx=5, columnspan=2, sticky='NSEW')
        self.file_1_browse_button = ttk.Button(top_rm_frame, text="Browse File 1",
                                               command=lambda: self.run(lambda: self.open_report_file(1),
                                                                        name='NoSync'))

        self.file2_filename = "Choose Second File to be Merged"
        self.filename_2_text = tk.StringVar()
        self.filename_2_text.set(self.file2_filename)
        self.filename_2_label = ttk.Label(top_rm_frame, style="File.TLabel", textvariable=self.filename_2_text)
        self.filename_2_label.grid(row=1, column=0, padx=5, columnspan=2, sticky='NSEW')
        self.file_2_browse_button = ttk.Button(top_rm_frame, text="Browse File 2",
                                               command=lambda: self.run(lambda: self.open_report_file(2),
                                                                        name='NoSync'))

        self.save_location_button = ttk.Button(lowest_rm_frame, text="Browse Save Location",
                                               command=lambda: self.run(lambda: self.prompt_save_location(),
                                                                        name='NoSync'))
        self.save_file_name_widget = tk.Text(lowest_rm_frame, height=1)
        self.save_file_name_widget.bind("<Tab>", self.focus_next_widget)
        self.save_file_name_label = ttk.Label(lowest_rm_frame, style="Notes.TLabel", text="Filename: ")

        self.join_type_label = ttk.Label(lower_middle_rm_frame, style="Notes.TLabel", text="Join Type: ")
        self.join_type_label.grid(column=0, row=0, padx=5, sticky="NSE")
        self.join_tip_text = tk.StringVar()
        self.join_tip_text.set(self.inner_join_tip)
        self.join_tip_label = ttk.Label(lower_rm_frame, style="Notes.TLabel", textvariable=self.join_tip_text)
        self.join_tip_label.grid(row=1, column=0, columnspan=2, padx=5, sticky='NSEW')
        self.joins = tk.StringVar()
        # self.joins.set("inner")
        self.join_type_inner_image_path = f'{os.curdir}/img/img_innerjoin.png'
        self.join_type_left_image_path = f'{os.curdir}/img/img_leftjoin.png'
        self.join_type_right_image_path = f'{os.curdir}/img/img_rightjoin.png'
        self.join_type_outer_image_path = f'{os.curdir}/img/img_fulljoin.png'
        self.join_type_append_image_path = f'{os.curdir}/img/img_append.png'
        if os.path.isfile(self.join_type_inner_image_path):
            print("File Found in current directory: " + self.join_type_inner_image_path)
        elif os.path.isfile(f'{os.pardir}/img/img_innerjoin.png'):
            print("File Found in parent directory: " + f'{os.pardir}/img/img_innerjoin.png')
            self.join_type_inner_image_path = f'{os.pardir}/img/img_innerjoin.png'
            self.join_type_left_image_path = f'{os.pardir}/img/img_leftjoin.png'
            self.join_type_right_image_path = f'{os.pardir}/img/img_rightjoin.png'
            self.join_type_outer_image_path = f'{os.pardir}/img/img_fulljoin.png'
            self.join_type_append_image_path = f'{os.pardir}/img/img_append.png'
        else:
            print("Could not find image directory")
        self.join_type_inner_image = Image.open(self.join_type_inner_image_path)
        self.join_type_left_image = Image.open(self.join_type_left_image_path)
        self.join_type_right_image = Image.open(self.join_type_right_image_path)
        self.join_type_outer_image = Image.open(self.join_type_outer_image_path)
        self.join_type_append_image = Image.open(self.join_type_append_image_path)
        self.join_type_inner_image = self.join_type_inner_image.resize((128, 93), Image.ANTIALIAS)
        self.join_type_left_image = self.join_type_left_image.resize((128, 93), Image.ANTIALIAS)
        self.join_type_right_image = self.join_type_right_image.resize((128, 93), Image.ANTIALIAS)
        self.join_type_outer_image = self.join_type_outer_image.resize((128, 93), Image.ANTIALIAS)
        self.join_type_append_image = self.join_type_append_image.resize((128, 93), Image.ANTIALIAS)
        self.join_type_inner_image_widget = ImageTk.PhotoImage(self.join_type_inner_image, master=lower_rm_frame)
        self.join_type_left_image_widget = ImageTk.PhotoImage(self.join_type_left_image, master=lower_rm_frame)
        self.join_type_right_image_widget = ImageTk.PhotoImage(self.join_type_right_image, master=lower_rm_frame)
        self.join_type_outer_image_widget = ImageTk.PhotoImage(self.join_type_outer_image, master=lower_rm_frame)
        self.join_type_append_image_widget = ImageTk.PhotoImage(self.join_type_append_image, master=lower_rm_frame)

        self.join_type_inner_image_panel = ttk.Label(lower_rm_frame, image=self.join_type_inner_image_widget,
                                                    anchor='center')
        self.join_type_left_image_panel = ttk.Label(lower_rm_frame, image=self.join_type_left_image_widget,
                                                    anchor='center')
        self.join_type_right_image_panel = ttk.Label(lower_rm_frame, image=self.join_type_right_image_widget,
                                                     anchor='center')
        self.join_type_outer_image_panel = ttk.Label(lower_rm_frame, image=self.join_type_outer_image_widget,
                                                     anchor='center')
        self.join_type_append_image_panel = ttk.Label(lower_rm_frame, image=self.join_type_append_image_widget,
                                                      anchor='center')
        self.join_type_inner_image_panel.grid(column=0, row=0, columnspan=2, padx=5,
                                              sticky='NSEW')
        self.joins_list = ttk.OptionMenu(lower_middle_rm_frame, self.joins, "inner", "inner", "outer", "left",
                                         "right",
                                         "append", command=self.join_type)
        self.export_option_rm = tk.StringVar()
        self.export_option_rm.set("CSV")
        self.export_type_rm = ttk.OptionMenu(lowest_rm_frame, self.export_option_rm, "CSV", "CSV", "Excel",
                                             command=self.set_rm_export)
        self.joins_list.grid(column=1, row=0, padx=(0, 100), sticky="NSW")

        self.run_merge = ttk.Button(lowest_rm_frame, style="Run.TButton", text="Merge",
                                    command=lambda: self.run(lambda: self.run_merge_report(), name='NoSync'))
        self.file_1_browse_button.grid(row=0, column=2, padx=5, sticky='NSEW')
        self.file_2_browse_button.grid(row=1, column=2, padx=5, sticky='NSEW')
        self.file1_columns_text = tk.StringVar()
        self.file1_columns_text.set("File 1 - Columns")
        self.file1_columns_label = ttk.Label(middle_rm_frame, style="Notes.TLabel",
                                             textvariable=self.file1_columns_text)
        self.file1_columns_label_type_title = ttk.Label(self.file1_title_columns_rm_frame, style="Notes.TLabel",
                                                        text="File 1 - Select Column Order & Type")
        self.file2_columns_text = tk.StringVar()
        self.file2_columns_text.set("File 2 - Columns")
        self.file2_columns_label = ttk.Label(middle_rm_frame, style="Notes.TLabel",
                                             textvariable=self.file2_columns_text)
        self.file2_columns_label_type_title = ttk.Label(self.file2_title_columns_rm_frame, style="Notes.TLabel",
                                                        text="File 2 - Select Column Order & Type")
        self.file1_keys = tk.StringVar()
        self.file1_keys.set("")
        self.file2_keys = tk.StringVar()
        self.file2_keys.set("")
        # self.scrollbar = Scrollbar(self.middle_rm_frame, orient=VERTICAL)
        self.file1_pk = tk.Listbox(middle_rm_frame, listvariable=self.file1_keys, selectmode=tk.MULTIPLE,
                                   exportselection=False)  # , yscrollcommand=self.scrollbar.set)
        self.file2_pk = tk.Listbox(middle_rm_frame, listvariable=self.file2_keys, selectmode=tk.MULTIPLE,
                                   exportselection=False)  # , yscrollcommand=self.scrollbar.set)
        '''self.file1_pk = DragDropListboxMulti(self.middle_rm_frame, listvariable=self.file1_keys, exportselection=0)
        self.file2_pk = DragDropListboxMulti(self.middle_rm_frame, listvariable=self.file2_keys, exportselection=0)'''
        self.file1_pk.bind('<<ListboxSelect>>', self.onselect_file1_pk)
        self.file2_pk.bind('<<ListboxSelect>>', self.onselect_file2_pk)
        self.file1_pk.configure(justify=tk.RIGHT)
        self.file2_pk.configure(justify=tk.RIGHT)
        self.file1_columns_label.grid(row=0, column=0, padx=5, sticky='NSEW')
        self.file2_columns_label.grid(row=0, column=1, padx=5, sticky='NSEW')
        self.file1_pk.grid(row=1, column=0, padx=5, pady=5, sticky='NSEW')
        self.file2_pk.grid(row=1, column=1, padx=5, pady=5, sticky='NSEW')
        self.file1_columns_label_type_title.grid(row=0, column=0, padx=5, sticky='NSEW')
        self.file2_columns_label_type_title.grid(row=0, column=0, padx=5, sticky='NSEW')
        self.run_merge.grid(row=0, column=4, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.run_merge["state"] = "disabled"
        self.export_type_rm.grid(row=0, column=2, columnspan=1, padx=5, pady=5, sticky='NSEW')
        # self.run_merge_excel.grid(row=0, column=4, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_location_button.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_file_name_label.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_file_name_widget.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky='NSEW')

    # Prompt user for save location for Report Merging
    def prompt_save_location(self):
        self.save_location = filedialog.askdirectory()
        self.status.set("{}".format("Will save report in: %s" % self.save_location))
        self.report_merger.set_save_directory(self.save_location)

    def onselect_file1_pk(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        indexes = w.curselection()
        # Removes Duplicates
        self.dtypes_list_remove(1)

        # print("Indexes: ", indexes)
        self.report_dtypes_f1 = []
        self.column_order_list_f1 = []
        print(self.report_dtypes_f1)
        # counter = len(self.dtypes_list_file1)
        # print("Counter starting at: ", counter)
        counter = 0
        for index in indexes:
            column_name = w.get(index)
            print('You selected item %d: "%s"' % (index, column_name))
            self.report_dtypes_f1.append(tk.StringVar())
            self.column_order_list_f1.append(tk.StringVar())
            self.report_dtypes_f1[counter].set("string")
            self.column_order_list_f1[counter].set(f"{counter}")
            # print("counter: ", counter)
            self.dtypes_list_append(1, counter, index, len(indexes), column_name)
            counter += 1

    def onselect_file2_pk(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        indexes = w.curselection()
        # Removes Duplicates
        self.dtypes_list_remove(2)

        # print("Indexes: ", indexes)
        self.report_dtypes_f2 = []
        self.column_order_list_f2 = []
        print(self.report_dtypes_f2)
        # counter = len(self.dtypes_list_file1)
        # print("Counter starting at: ", counter)
        counter = 0
        for index in indexes:
            column_name = w.get(index)
            print('You selected item %d: "%s"' % (index, column_name))
            self.report_dtypes_f2.append(tk.StringVar())
            self.column_order_list_f2.append(tk.StringVar())
            self.report_dtypes_f2[counter].set("string")
            self.column_order_list_f2[counter].set(f"{counter}")
            # print("counter: ", counter)
            self.dtypes_list_append(2, counter, index, len(indexes), column_name)
            counter += 1

    def dtypes_list_append(self, file_num, counter, index, index_length, column_name):
        # Check if this is the first or second file we are working with.
        if file_num == 1:
            self.dtypes_list_file1.append([index,
                                           ttk.OptionMenu(self.file1_title_columns_rm_frame,
                                                          self.column_order_list_f1[counter],
                                                          tk.IntVar().set(0),
                                                          *list(range(0, index_length)),
                                                          command=lambda value: self.run(
                                                              lambda: self.column_order(value, counter, index, 1),
                                                              name='NoSync')),
                                           ttk.Label(self.file1_title_columns_rm_frame, style="Notes.TLabel",
                                                     text=f"{column_name}"),
                                           ttk.OptionMenu(self.file1_title_columns_rm_frame,
                                                          self.report_dtypes_f1[counter],
                                                          "string", "string",
                                                          "date", "int",
                                                          command=lambda value: self.run(
                                                              lambda: self.dtype_type(value, column_name, 1),
                                                              name='NoSync')),
                                           counter])
            # Set New Index Size On All of Rows
            # Regrid All Columns
            self.dtypes_list_file1[len(self.dtypes_list_file1) - 1][1].grid(row=len(self.dtypes_list_file1) - 1,
                                                                            column=0, padx=5, pady=5, sticky='NSEW')
            self.dtypes_list_file1[len(self.dtypes_list_file1) - 1][2].grid(row=len(self.dtypes_list_file1) - 1,
                                                                            column=1, padx=5, pady=5, sticky='NSEW')
            self.dtypes_list_file1[len(self.dtypes_list_file1) - 1][3].grid(row=len(self.dtypes_list_file1) - 1,
                                                                            column=2, padx=5, pady=5, sticky='NSEW')
            print("DTYPE LIST: ", self.dtypes_list_file1)
        elif file_num == 2:
            self.dtypes_list_file2.append([index,
                                           ttk.OptionMenu(self.file2_title_columns_rm_frame,
                                                          self.column_order_list_f2[counter],
                                                          tk.IntVar().set(0),
                                                          *list(range(0, index_length)),
                                                          command=lambda value: self.run(
                                                              lambda: self.column_order(value, counter, index, 2),
                                                              name='NoSync')),
                                           ttk.Label(self.file2_title_columns_rm_frame, style="Notes.TLabel",
                                                     text=f"{column_name}"),
                                           ttk.OptionMenu(self.file2_title_columns_rm_frame,
                                                          self.report_dtypes_f2[counter],
                                                          "string", "string",
                                                          "date", "int",
                                                          command=lambda value: self.run(
                                                              lambda: self.dtype_type(value, column_name, 2),
                                                              name='NoSync')),
                                           counter])
            # Set New Index Size On All of Rows
            # Regrid All Columns
            self.dtypes_list_file2[len(self.dtypes_list_file2) - 1][1].grid(row=len(self.dtypes_list_file2) - 1,
                                                                            column=0, padx=5, pady=5, sticky='NSEW')
            self.dtypes_list_file2[len(self.dtypes_list_file2) - 1][2].grid(row=len(self.dtypes_list_file2) - 1,
                                                                            column=1, padx=5, pady=5, sticky='NSEW')
            self.dtypes_list_file2[len(self.dtypes_list_file2) - 1][3].grid(row=len(self.dtypes_list_file2) - 1,
                                                                            column=2, padx=5, pady=5, sticky='NSEW')
            print("DTYPE LIST: ", self.dtypes_list_file2)

    def dtypes_list_remove(self, file_num):
        # If there are already elements in dtypes_list, then only remove the indexes that were unselected, this works.
        x = 0
        if file_num == 1:
            for dtype in self.dtypes_list_file1:
                print(f"Destroyed: {dtype} Length of File = {len(self.dtypes_list_file1)} counter = {x}")
                widget1 = dtype[1]
                widget1.destroy()
                widget2 = dtype[2]
                widget2.destroy()
                widget3 = dtype[3]
                widget3.destroy()
                # del self.dtypes_list_file1[x]
                x += 1
            self.dtypes_list_file1.clear()
            self.dtypes_list_file1 = []
        elif file_num == 2:
            for dtype in self.dtypes_list_file2:
                print(f"Destroyed: {dtype} Length of File = {len(self.dtypes_list_file2)} counter = {x}")
                widget1 = dtype[1]
                widget1.destroy()
                widget2 = dtype[2]
                widget2.destroy()
                widget3 = dtype[3]
                widget3.destroy()
                # del self.dtypes_list_file1[x]
                x += 1
            self.dtypes_list_file2.clear()
            self.dtypes_list_file2 = []

    def column_order(self, value, column_num, index, file_num):
        self.status.set("{}".format("Selected Column Order: %s" % value))
        if file_num == 1:
            print("List Before Change: ", self.dtypes_list_file1[column_num])
            # Capture Old Value Before Changing
            old_value = self.dtypes_list_file1[column_num][4]
            # Look for any other duplicates and changes those to the old value.
            for x in range(0, len(self.dtypes_list_file1)):
                print(f"Searching Value: {self.dtypes_list_file1[x][4]}={value}")
                if self.dtypes_list_file1[x][4] == value and self.dtypes_list_file1[x][0] != index:
                    print(f"Value found: {self.dtypes_list_file1[x][4]}={value}")
                    self.column_order_list_f1[x].set(old_value)
                    self.dtypes_list_file1[x][4] = old_value
            # Update Value to new value
            self.dtypes_list_file1[column_num][4] = value
            print("List After Change: ", self.dtypes_list_file1[column_num])
        elif file_num == 2:
            print("List Before Change: ", self.dtypes_list_file2[column_num])
            # Capture Old Value Before Changing
            old_value = self.dtypes_list_file2[column_num][4]
            # Look for any other duplicates and changes those to the old value.
            for x in range(0, len(self.dtypes_list_file2)):
                print(f"Searching Value: {self.dtypes_list_file2[x][4]}={value}")
                if self.dtypes_list_file2[x][4] == value and self.dtypes_list_file2[x][0] != index:
                    print(f"Value found: {self.dtypes_list_file2[x][4]}={value}")
                    self.column_order_list_f2[x].set(old_value)
                    self.dtypes_list_file2[x][4] = old_value
            # Update Value to new value
            self.dtypes_list_file2[column_num][4] = value
            print("List After Change: ", self.dtypes_list_file2[column_num])

    def column_sort(self, file):
        if file == 1:
            print("List Before Sort: ", self.dtypes_list_file1)
            self.dtypes_list_file1 = sorted(self.dtypes_list_file1, key=lambda x: x[4])
            print("List After Sort: ", self.dtypes_list_file1)
        elif file == 2:
            print("List Before Sort: ", self.dtypes_list_file2)
            self.dtypes_list_file2 = sorted(self.dtypes_list_file2, key=lambda x: x[4])
            print("List After Sort: ", self.dtypes_list_file2)

    def dtype_type(self, data_type, column, file):
        self.status.set("{}".format("Selected Data Type: %s" % data_type))
        error = self.report_merger.set_columndtype(file, column, data_type)
        if error == 0:
            self.status.set(f'Column "{column}" successfully changed to {data_type}')
        elif error == 1:
            self.status.set(f'Column "{column}" could not be changed to {data_type}')

    # Chooses export type
    def set_rm_export(self, value):
        if value == 'CSV':
            self.csv_flag_rm = 1
        else:
            self.csv_flag_rm = 0

        # Opens Report Merger File for Both Files Depending on "number", which is for file 1 or file 2

    def open_report_file(self, number):
        if number == 1:
            self.file_1_browse_button["state"] = "disabled"
            print("Selecting File 1")
            self.file1_filename = filedialog.askopenfilename(initialdir="/", title="Select A Report", filetypes=(
                ("Excel File", "*.xlsx;*xls;*csv"), ("Other Excel Files", "*.xlsm,*.xltx,*.xltm,*.csv")))
            self.filename_1_text.set(self.file1_filename)
            if self.filename_1_text.get() == "":
                self.filename_1_text.set("No File Selected")
                self.file_1_browse_button["state"] = "normal"
                return 1
            print("Gathered Filename: ", self.file1_filename)
            self.filename_1_text.set("{}".format("%s" % self.file1_filename))
            self.status.set(f"Selected File: {self.file1_filename}")
            self.report_merger.set_file_1(self.file1_filename)
            self.status.set("Loading File")
            self.report_merger.load_dataframe_1()
            self.status.set("Populating List")
            string1 = self.report_merger.get_features(self.report_merger.get_df1())
            self.file1_keys.set(string1)
            self.file_1_browse_button["state"] = "normal"
        elif number == 2:
            self.file_2_browse_button["state"] = "disabled"
            print("Selecting File 2")
            self.file2_filename = filedialog.askopenfilename(initialdir="/", title="Select A Report", filetypes=(
                ("Excel File", "*.xlsx;*xls;*csv"), ("Other Excel Files", "*.xlsm,*.xltx,*.xltm,*.csv")))
            self.filename_2_text.set(self.file2_filename)
            if self.filename_2_text.get() == "":
                self.filename_2_text.set("No File Selected")
                self.file_2_browse_button["state"] = "normal"
                return 1
            print("Gathered Filename: ", self.file2_filename)
            self.filename_2_text.set("{}".format("%s" % self.file2_filename))
            self.status.set(f"Selected File: {self.file2_filename}")
            self.report_merger.set_file_2(self.file2_filename)
            self.status.set("Loading File")
            self.report_merger.load_dataframe_2()
            self.status.set("Populating List")
            string2 = self.report_merger.get_features(self.report_merger.get_df2())
            self.file2_keys.set(string2)
            self.file_2_browse_button["state"] = "normal"
        if self.filename_1_text.get() in (
                "No File Selected", "Choose First File to be Merged") or self.filename_2_text.get() in (
                "No File Selected", "Choose Second File to be Merged"):
            print("Entered")
            self.run_merge["state"] = "disabled"
        else:
            self.run_merge["state"] = "normal"

    def join_type(self, value):
        self.status.set(f"Selected Join Type: {value}")
        self.report_merger.set_join_type(value)
        if value == "inner":
            self.join_tip_text.set(self.inner_join_tip)
            self.join_type_inner_image_panel.grid(column=0, row=0, padx=5, columnspan=2, sticky='NSEW')
            self.join_type_left_image_panel.grid_forget()
            self.join_type_right_image_panel.grid_forget()
            self.join_type_outer_image_panel.grid_forget()
            self.join_type_append_image_panel.grid_forget()
        elif value == "left":
            self.join_tip_text.set(self.left_join_tip)
            self.join_type_left_image_panel.grid(column=0, row=0, padx=5, columnspan=2, sticky='NSEW')
            self.join_type_inner_image_panel.grid_forget()
            self.join_type_right_image_panel.grid_forget()
            self.join_type_outer_image_panel.grid_forget()
            self.join_type_append_image_panel.grid_forget()
        elif value == "right":
            self.join_tip_text.set(self.right_join_tip)
            self.join_type_right_image_panel.grid(column=0, row=0, padx=5, columnspan=2, sticky='NSEW')
            self.join_type_left_image_panel.grid_forget()
            self.join_type_inner_image_panel.grid_forget()
            self.join_type_outer_image_panel.grid_forget()
            self.join_type_append_image_panel.grid_forget()
        elif value == "outer":
            self.join_tip_text.set(self.outer_join_tip)
            self.join_type_outer_image_panel.grid(column=0, row=0, padx=5, columnspan=2, sticky='NSEW')
            self.join_type_left_image_panel.grid_forget()
            self.join_type_right_image_panel.grid_forget()
            self.join_type_inner_image_panel.grid_forget()
            self.join_type_append_image_panel.grid_forget()
        elif value == "append":
            self.join_tip_text.set(self.append_join_tip)
            self.join_type_append_image_panel.grid(column=0, row=0, padx=5, columnspan=2, sticky='NSEW')
            self.join_type_inner_image_panel.grid_forget()
            self.join_type_left_image_panel.grid_forget()
            self.join_type_right_image_panel.grid_forget()
            self.join_type_outer_image_panel.grid_forget()

    # Run's the report merging and export process!
    # Future Improvements: Preview Joined Dataframe on Menu
    def run_merge_report(self):
        self.run_merge["state"] = "disabled"
        # th = threading.current_thread()
        res_list1 = []
        res_list2 = []
        report_name = self.save_file_name_widget.get("1.0", "end-1c")
        self.report_merger.set_report_name(report_name)
        if self.report_merger.get_join_type() == "append":
            self.status.set("{}".format("Running Merge, Please Be Patient (Bigger File = More Time)"))
            self.report_merger.join_data(res_list1, res_list2)
            self.status.set("{}".format("Exporting Data..."))
            # csv_flag = 1
            self.report_merger.export_data(self.csv_flag_rm)
            self.status.set(f"Export Complete! Please find that report in {self.save_location}")
        else:
            # Check if there are columns chosen
            if self.dtypes_list_file1 and self.dtypes_list_file2:
                # Check if dtypes indexing is sorted.
                self.column_sort(1)
                self.column_sort(2)
                for dtype in self.dtypes_list_file1:
                    entry_1 = dtype[2].cget("text")
                    res_list1.append(entry_1)
                for dtype in self.dtypes_list_file2:
                    entry_2 = dtype[2].cget("text")
                    res_list2.append(entry_2)
                print(res_list1)
                print(res_list2)
                self.report_merger.set_df1_join_keys(res_list1)
                self.report_merger.set_df2_join_keys(res_list2)
                self.status.set("{}".format("Running Merge, Please Be Patient (Bigger File = More Time)"))
                self.report_merger.join_data()
                self.status.set("{}".format("Exporting Data..."))
                self.report_merger.export_data(self.csv_flag_rm)
                self.status.set(f'Exported Successfully: {self.save_location}')
            else:
                print("Select a Join Key!")
                self.status.set("{}".format("Select a column to join on (Join Key Required)!"))
        self.run_merge["state"] = "normal"


# Analytical Profiler Class
class AnalyticalProfilerFrame(tk.Frame):
    analytical_profiler = None
    log = None
    tabControl = None
    analytical_profiler_frame = None
    status = None
    csv_flag_rm = 1
    save_location = os.getcwd()
    file_filename = "Choose File to be Analyzed"
    filename_text = None
    titleAPFrame = None
    topAPFrame = None
    middleAPFrame = None
    lower_middleAPFrame = None
    lowerAPFrame = None
    lowestAPFrame = None
    filename_label = None
    file_browse_button = None
    save_location_button = None
    run_analysis_button = None
    export_button = None
    save_file_name_widget = None
    save_file_name_label = None
    export_option_rm = None
    export_type_rm = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        self.analytical_profiler = ReportAnalyzer(self.log)
        self.draw_frame()
        self.tabControl.add(self.analytical_profiler_frame, text="Analytic Profiler")
        tk.Frame.__init__(self, self.analytical_profiler_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    def draw_frame(self):
        # Setting up Frames in Report Merger Tab
        self.analytical_profiler_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.analytical_profiler_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.analytical_profiler_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.analytical_profiler_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.analytical_profiler_frame, 0, minsize=1, weight=1)
        self.titleAPFrame = ttk.Frame(self.analytical_profiler_frame, style="Top.TFrame")
        self.topAPFrame = ttk.Frame(self.analytical_profiler_frame)
        self.middleAPFrame = ttk.Frame(self.analytical_profiler_frame)
        self.lower_middleAPFrame = ttk.Frame(self.analytical_profiler_frame)
        self.lowerAPFrame = ttk.Frame(self.analytical_profiler_frame)
        self.lowestAPFrame = ttk.Frame(self.analytical_profiler_frame)
        tk.Grid.rowconfigure(self.titleAPFrame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.titleAPFrame, 0, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.topAPFrame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.topAPFrame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.topAPFrame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.topAPFrame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.middleAPFrame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.middleAPFrame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.middleAPFrame, 2, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.middleAPFrame, 3, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.middleAPFrame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middleAPFrame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.lower_middleAPFrame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.lower_middleAPFrame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lower_middleAPFrame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.lower_middleAPFrame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.lowerAPFrame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.lowerAPFrame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lowerAPFrame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.lowerAPFrame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.lowestAPFrame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lowestAPFrame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lowestAPFrame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.lowestAPFrame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lowestAPFrame, 3, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.lowestAPFrame, 4, minsize=1, weight=0)
        self.titleAPFrame.grid(column=0, row=0, sticky='NSEW')
        self.topAPFrame.grid(column=0, row=1, sticky='NSEW')
        self.middleAPFrame.grid(column=0, row=2, sticky='NSEW')
        self.lower_middleAPFrame.grid(column=0, row=4, sticky='NSEW')
        self.lowerAPFrame.grid(column=0, row=5, sticky='NSEW')
        self.lowestAPFrame.grid(column=0, row=6, sticky='NSEW')

        # Set the Buttons for the Report Merger class
        self.file_filename = "Choose file to be analyzed"
        self.filename_text = tk.StringVar()
        self.filename_text.set(self.file_filename)
        self.filename_label = ttk.Label(self.topAPFrame, style="File.TLabel", textvariable=self.filename_text)
        self.filename_label.grid(row=0, column=0, padx=5, columnspan=2, sticky='NSEW')
        self.file_browse_button = ttk.Button(self.topAPFrame, text="Browse File",
                                             command=lambda: self.run(lambda: self.open_report_file(),
                                                                      name='NoSync'))
        self.save_location_button = ttk.Button(self.lowestAPFrame, text="Browse Save Location",
                                               command=lambda: self.run(lambda: self.prompt_save_location(),
                                                                        name='NoSync'))
        self.run_analysis_button = ttk.Button(self.lowestAPFrame, text="Run Analysis",
                                              command=lambda: self.run(lambda: self.run_pandas_profiling(),
                                                                       name='NoSync'))
        self.export_button = ttk.Button(self.lowestAPFrame, text="Export Analysis",
                                        command=lambda: self.run(lambda: self.export_analysis(),
                                                                 name='NoSync'))
        self.save_file_name_widget = tk.Text(self.lowestAPFrame, height=1)
        self.save_file_name_widget.bind("<Tab>", self.focus_next_widget)
        self.save_file_name_label = ttk.Label(self.lowestAPFrame, style="Notes.TLabel", text="Filename: ")

        self.export_option_rm = tk.StringVar()
        self.export_option_rm.set("CSV")
        self.export_type_rm = ttk.OptionMenu(self.lowestAPFrame, self.export_option_rm, "CSV", "CSV", "Excel",
                                             command=self.set_rm_export)
        self.file_browse_button.grid(row=0, column=2, padx=5, sticky='NSEW')
        self.export_type_rm.grid(row=0, column=2, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_location_button.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.run_analysis_button.grid(row=0, column=4, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_file_name_label.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky='NSEW')
        self.save_file_name_widget.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky='NSEW')

    # Prompt user for save location for Report Merging
    def prompt_save_location(self):
        self.save_location = filedialog.askdirectory()
        self.status.set("{}".format("Will save report in: %s" % self.save_location))
        self.analytical_profiler.set_save_directory(self.save_location)

    # Chooses export type
    def set_rm_export(self, value):
        if value == 'CSV':
            self.csv_flag_rm = 1
        else:
            self.csv_flag_rm = 0

    def open_report_file(self):
        self.file_browse_button["state"] = "disabled"
        print("Selecting File 1")
        self.file_filename = filedialog.askopenfilename(initialdir="/", title="Select A Report", filetypes=(
            ("Excel File", "*.xlsx;*xls;*csv"), ("Other Excel Files", "*.xlsm,*.xltx,*.xltm,*.csv")))
        self.filename_text.set(self.file_filename)
        if self.filename_text.get():
            self.analytical_profiler.set_file(self.filename_text.get())
            self.analytical_profiler.load_dataframe()
            print("File selected")
            # Custom Report
            self.status.set("{}".format("Running Visualizer and Data Modeler"))
            test_success = self.analytical_profiler.run_analysis()
            if test_success == 0:
                self.status.set(f"Visualization Complete")
            else:
                self.status.set(f"File Could not be Visualized, but Pandas Profiling may still work")
        else:
            self.filename_text.set("No File Selected")
            self.file_browse_button["state"] = "normal"
            return 1
        print("Gathered Filename: ", self.file_filename)
        self.filename_text.set("{}".format("%s" % self.file_filename))
        self.status.set("{}".format("Selected File: %s" % self.file_filename))
        self.status.set("{}".format("Loading File"))
        self.status.set("{}".format("Populating List"))
        self.file_browse_button["state"] = "normal"

    def run_pandas_profiling(self):
        # Set Parameters like Report Name, and paths for export
        report_name = self.save_file_name_widget.get("1.0", "end-1c")
        report_title = report_name

        # Pandas Profiling
        self.analytical_profiler.set_report_title(report_title)
        self.analytical_profiler.set_report_name(report_name)
        sample_flag = None  # Set to the sample size if you would like to do it on a sample instead.
        minimal_flag = False  # Quicker run if set to true, but not everything is captured.
        self.status.set(f"Running Pandas Profiling")
        self.analytical_profiler.create_report(sample_flag, minimal_flag)
        self.analytical_profiler.export_report()
        self.status.set(f"Analysis Complete!")

    def export_analysis(self):
        print("Implement this")


# Twitter Archive Class
class TwitterArchiveFrame(tk.Frame):
    url_list_twitter_archive = []
    log = None
    tabControl = None
    twitter_archive_frame = None
    status = None
    save_location = None
    progress_bar_twitter_archive = None
    progress_bar_value_twitter_archive = 0
    progress_bar_max_value_twitter_archive = 0
    twitter_add_url_button = None
    twitter_remove_url_button = None
    twitter_openfile_button = None
    twitter_save_location_button = None
    twitter_archive_button = None
    twitter_queue_title = None
    twitter_queue_title_label = None
    twitter_config_title = None
    twitter_config_title_label = None
    twitter_config_screenshot_value = None
    twitter_config_screenshot = None
    twitter_screenshot_filetype_title = None
    twitter_screenshot_filetype = None
    twitter_screenshot_filetype_menu = None
    twitter_screenshot_size_title = None
    twitter_screenshot_size = None
    twitter_screenshot_size_menu = None
    twitter_screenshot_quality_title = None
    twitter_screenshot_quality_value = None
    twitter_screenshot_quality = None
    twitter_zoom_title = None
    twitter_zoom_value = None
    twitter_zoom = None
    twitter_config_html_dl_value = None
    twitter_config_html_dl = None
    twitter_config_compress_value = None
    twitter_config_compress = None
    twitter_config_twitter_value = None
    twitter_config_twitter = None
    twitter_links_text = None
    twitter_links_label = None
    twitter_url_listbox = None
    twitter_url_entry = None
    twitter_percentage_text = None
    twitter_percentage_title = None
    twitter_percentage_label = None
    twitter_percentage_title_label = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        # self.twitter_archive = TwitterDownloader(self.log)
        self.draw_frame()
        self.tabControl.add(self.twitter_archive_frame, text="Twitter Archive")
        tk.Frame.__init__(self, self.twitter_archive_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    def draw_frame(self):
        self.twitter_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.twitter_archive_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.twitter_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.twitter_archive_frame, 1, minsize=1, weight=1)
        twitter_archive_selection_frame = ttk.Frame(self.twitter_archive_frame)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(twitter_archive_selection_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(twitter_archive_selection_frame, 0, minsize=1, weight=1)
        twitter_archive_config_frame = ttk.Frame(self.twitter_archive_frame)
        tk.Grid.rowconfigure(twitter_archive_config_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(twitter_archive_config_frame, 0, minsize=1, weight=0)
        top_twitter_frame = ttk.Frame(twitter_archive_selection_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(top_twitter_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_twitter_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_twitter_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_twitter_frame, 0, minsize=1, weight=1)
        middle_twitter_button_frame = ttk.Frame(twitter_archive_selection_frame)
        tk.Grid.rowconfigure(middle_twitter_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(middle_twitter_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_twitter_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_twitter_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_twitter_button_frame, 3, minsize=1, weight=1)
        middle_twitter_frame = ttk.Frame(twitter_archive_selection_frame)
        tk.Grid.rowconfigure(middle_twitter_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_twitter_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_twitter_frame, 0, minsize=1, weight=1)
        bottom_twitter_frame = ttk.Frame(twitter_archive_selection_frame)
        tk.Grid.rowconfigure(bottom_twitter_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_twitter_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_twitter_frame, 1, minsize=1, weight=1)
        # tk.Grid.rowconfigure(self.notification_frame, 0, minsize=1, weight=1)
        # tk.Grid.columnconfigure(self.notification_frame, 0, minsize=1, weight=1)
        # Buttons
        self.twitter_add_url_button = ttk.Button(middle_twitter_button_frame, text="Add", style='Add.TButton', width=9,
                                                 command=self.add_webarchive_url)
        self.twitter_add_url_button.grid(column=0, row=1, sticky='NSEW', padx=5, pady=10)
        self.twitter_remove_url_button = ttk.Button(middle_twitter_button_frame, text="Remove", style='Remove.TButton',
                                                    width=9, command=self.remove_webarchive_url)
        self.twitter_remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=5, pady=10)
        self.twitter_openfile_button = ttk.Button(middle_twitter_button_frame, text="Open File", style='Open.TButton',
                                                  width=9, command=self.open_file_webarchive)
        self.twitter_openfile_button.grid(column=2, row=1, sticky='NSEW', padx=5, pady=10)
        self.twitter_save_location_button = ttk.Button(middle_twitter_button_frame, text="Save Location", width=15,
                                                       command=self.choose_save_location_twitter)
        self.twitter_save_location_button.grid(column=3, row=1, sticky='NSEW', padx=5, pady=10)
        self.twitter_archive_button = ttk.Button(bottom_twitter_frame, text="Begin Archive",
                                                 command=lambda: self.run(lambda: self.download_tweets(),
                                                                          name='NoSync'))
        self.twitter_archive_button.grid(column=0, row=3, columnspan=2, sticky='NSEW', padx=15, pady=10)

        # Labels
        # self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.twitter_queue_title = tk.StringVar()
        self.twitter_queue_title.set("Download Queue")
        self.twitter_queue_title_label = ttk.Label(middle_twitter_frame,
                                                   textvariable=self.twitter_queue_title,
                                                   style="Notes.TLabel")
        self.twitter_queue_title_label.grid(column=0, row=0, columnspan=1)
        self.twitter_config_title = tk.StringVar()
        self.twitter_config_title.set("Configure Archive")
        self.twitter_config_title_label = ttk.Label(twitter_archive_config_frame,
                                                    textvariable=self.twitter_config_title,
                                                    style="Notes.TLabel")
        self.twitter_config_title_label.grid(column=0, row=0, columnspan=2, pady=(5, 5), sticky='NSEW')
        self.twitter_config_screenshot_value = tk.IntVar()
        self.twitter_config_screenshot_value.set(1)
        self.twitter_config_screenshot = ttk.Checkbutton(twitter_archive_config_frame, text="Capture Screenshot",
                                                         variable=self.twitter_config_screenshot_value, onvalue=1,
                                                         offvalue=0,
                                                         style="TCheckbutton", command=self.onclick_capture_screenshot)
        self.twitter_config_screenshot.grid(column=0, row=1, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_screenshot_filetype_title = ttk.Label(twitter_archive_config_frame, text="File Type",
                                                           style="Notes.TLabel")
        self.twitter_screenshot_filetype_title.grid(column=0, row=2, columnspan=1, padx=(5, 5), pady=(5, 5),
                                                    sticky='NSEW')
        self.twitter_screenshot_filetype = tk.StringVar()
        self.twitter_screenshot_filetype.set("PNG")  # default value
        self.twitter_screenshot_filetype_menu = ttk.OptionMenu(twitter_archive_config_frame,
                                                               self.twitter_screenshot_filetype,
                                                               "PNG", "PNG", "JPEG")
        self.twitter_screenshot_filetype_menu.grid(column=1, row=2, columnspan=1, padx=(5, 5), pady=(5, 5),
                                                   sticky='NSEW')
        self.twitter_screenshot_size_title = ttk.Label(twitter_archive_config_frame, text="Size",
                                                       style="Notes.TLabel")
        self.twitter_screenshot_size_title.grid(column=0, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_screenshot_size = tk.StringVar()
        self.twitter_screenshot_size.set("Full")  # default value
        self.twitter_screenshot_size_menu = ttk.OptionMenu(twitter_archive_config_frame, self.twitter_screenshot_size,
                                                           "Full", "Full", "Normal")
        self.twitter_screenshot_size_menu.grid(column=1, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_screenshot_quality_title = ttk.Label(twitter_archive_config_frame, text="Quality",
                                                          style="Notes.TLabel")
        self.twitter_screenshot_quality_title.grid(column=0, row=4, columnspan=1, padx=(5, 5), pady=(5, 5),
                                                   sticky='NSEW')
        self.twitter_screenshot_quality_value = tk.IntVar()
        self.twitter_screenshot_quality_value.set(100)
        self.twitter_screenshot_quality = tk.Scale(twitter_archive_config_frame, from_=10, to=100,
                                                   variable=self.twitter_screenshot_quality_value, orient=tk.HORIZONTAL)
        self.twitter_screenshot_quality.grid(column=1, row=4, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_config_html_dl_value = tk.IntVar()
        self.twitter_config_html_dl = ttk.Checkbutton(twitter_archive_config_frame, text="Archive Website",
                                                      variable=self.twitter_config_html_dl_value, onvalue=1, offvalue=0,
                                                      style="TCheckbutton")
        self.twitter_config_html_dl.grid(column=0, row=6, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_config_compress_value = tk.IntVar()
        self.twitter_config_compress = ttk.Checkbutton(twitter_archive_config_frame, text="Compress/Zip",
                                                       variable=self.twitter_config_compress_value, onvalue=1,
                                                       offvalue=0,
                                                       style="TCheckbutton")
        self.twitter_config_compress.grid(column=0, row=7, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_config_twitter_value = tk.IntVar()
        self.twitter_config_twitter = ttk.Checkbutton(twitter_archive_config_frame, text="Twitter to CSV",
                                                      variable=self.twitter_config_twitter_value, onvalue=1, offvalue=0,
                                                      style="TCheckbutton")
        self.twitter_config_twitter.grid(column=0, row=8, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.twitter_links_text = tk.StringVar()
        self.twitter_links_text.set(r'Enter Web Link(s) ⮟')
        self.twitter_links_label = ttk.Label(top_twitter_frame, textvariable=self.twitter_links_text,
                                             style="Notes.TLabel")
        self.twitter_links_label.grid(column=0, row=0, columnspan=1, sticky='W')
        self.twitter_percentage_text = tk.StringVar()
        self.twitter_percentage_text.set((
            f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
            f"{(self.progress_bar_value_twitter_archive / (self.progress_bar_max_value_twitter_archive + 1)) * 100}%"))
        self.twitter_percentage_label = ttk.Label(bottom_twitter_frame, textvariable=self.twitter_percentage_text,
                                                  style="Notes.TLabel")
        self.twitter_percentage_label.grid(column=0, row=2, columnspan=2)
        self.twitter_percentage_title = tk.StringVar()
        self.twitter_percentage_title.set("Percentage")
        self.twitter_percentage_title_label = ttk.Label(bottom_twitter_frame,
                                                        textvariable=self.twitter_percentage_title,
                                                        style="Notes.TLabel")
        self.twitter_percentage_title_label.grid(column=0, row=0, columnspan=2)

        # ListBox
        self.twitter_url_listbox = tk.Listbox(middle_twitter_frame, height=12, selectmode='multiple', exportselection=0)
        self.twitter_url_listbox.grid(column=0, row=1, columnspan=2, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.twitter_url_listbox, 0, weight=1)

        # Entries
        self.twitter_url_entry = tk.Text(top_twitter_frame, height=9)
        self.twitter_url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_webarchive_list()
        self.twitter_url_entry.grid(column=0, row=2, columnspan=2, sticky='NSEW')

        # Progress Bar
        self.progress_bar_twitter_archive = ttk.Progressbar(
            bottom_twitter_frame, orient="horizontal",
            mode="determinate"
        )
        twitter_archive_selection_frame.grid(column=1, row=0, columnspan=1, sticky='NSEW')
        twitter_archive_config_frame.grid(column=0, row=0, columnspan=1, sticky='NSEW')
        self.progress_bar_twitter_archive.grid(column=0, row=1, padx=15, pady=10, columnspan=2, sticky='NSEW')
        top_twitter_frame.grid(row=1, column=0, sticky='NSEW')
        middle_twitter_button_frame.grid(row=2, column=0, sticky='NSEW')
        middle_twitter_frame.grid(row=3, column=0, sticky='NSEW')
        bottom_twitter_frame.grid(row=4, column=0, sticky='NSEW')

    def download_tweets(self):
        self.url_list_twitter_archive = list(filter(None, self.url_list_twitter_archive))
        self.url_list_twitter_archive = list(dict.fromkeys(self.url_list_twitter_archive))
        self.progress_bar_max_value_twitter_archive = len(self.url_list_twitter_archive)
        if self.progress_bar_max_value_twitter_archive > 0:
            self.status.set(f'Downloading {len(self.url_list_twitter_archive)} URL(s)')
            self.twitter_archive_button["state"] = "disabled"
            self.twitter_add_url_button["state"] = "disabled"
            self.twitter_remove_url_button["state"] = "disabled"
            self.twitter_openfile_button["state"] = "disabled"
            self.twitter_save_location_button["state"] = "disabled"
            self.progress_bar_value_twitter_archive = 0
            self.progress_bar_twitter_archive['maximum'] = self.progress_bar_max_value_twitter_archive
            self.progress_bar_twitter_archive['value'] = 0
            print(f'{self.progress_bar_max_value_twitter_archive}:MAX VALUE')
            self.twitter_percentage_text.set((
                f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
                f"{math.ceil((self.progress_bar_value_twitter_archive / self.progress_bar_max_value_twitter_archive) * 100)}%"))
            i = 0
            for url in self.url_list_twitter_archive:
                TwitterDownloader(tweet_url=url, output_dir=self.save_location, logger=self.log).download()
                self.progress_bar_value_twitter_archive = i + 1
                self.twitter_percentage_text.set((
                    f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
                    f"{math.ceil((self.progress_bar_value_twitter_archive / self.progress_bar_max_value_twitter_archive) * 100)}",
                    f"%"))
                self.progress_bar_twitter_archive['value'] = i + 1
                print("Value: ", self.progress_bar_value_twitter_archive)
                print("Max Value: ", self.progress_bar_max_value_twitter_archive)
                self.status.set(
                    f'Completed {self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive}')
                i += 1
            self.tabControl.tab(1, state="normal")
            self.tabControl.tab(2, state="normal")
            self.twitter_archive_button["state"] = "enabled"
            self.twitter_add_url_button["state"] = "enabled"
            self.twitter_remove_url_button["state"] = "enabled"
            self.twitter_openfile_button["state"] = "enabled"
            self.twitter_save_location_button["state"] = "enabled"
            self.status.set(f'Downloaded {self.progress_bar_value_twitter_archive} website screenshot(s)!')
        else:
            print("No Website Links Added")
            self.status.set(f'Add Some Website Links First!')

    def onclick_capture_screenshot(self):
        value = self.twitter_config_screenshot_value.get()
        if value == 0:
            self.twitter_screenshot_filetype_title.grid_forget()
            self.twitter_screenshot_filetype_menu.grid_forget()
            self.twitter_screenshot_size_title.grid_forget()
            self.twitter_screenshot_size_menu.grid_forget()
            self.twitter_screenshot_quality_title.grid_forget()
            self.twitter_screenshot_quality.grid_forget()
        elif value == 1:
            self.twitter_screenshot_filetype_title.grid(column=0, row=2, columnspan=1, padx=(5, 0), pady=(5, 5),
                                                        sticky='NSEW')
            self.twitter_screenshot_filetype_menu.grid(column=1, row=2, columnspan=1, padx=(5, 5), pady=(5, 5),
                                                       sticky='NSEW')
            self.twitter_screenshot_size_title.grid(column=0, row=3, columnspan=1, padx=(5, 0), pady=(0, 5),
                                                    sticky='NSEW')
            self.twitter_screenshot_size_menu.grid(column=1, row=3, columnspan=1, padx=(5, 5), pady=(0, 5),
                                                   sticky='NSEW')
            self.twitter_screenshot_quality_title.grid(column=0, row=4, columnspan=1, padx=(5, 0), pady=(0, 5),
                                                       sticky='NSEW')
            self.twitter_screenshot_quality.grid(column=1, row=4, columnspan=1, padx=(5, 5), pady=(0, 5), sticky='NSEW')

    def choose_save_location_twitter(self):
        self.save_location = tk.filedialog.askdirectory()
        print("Save Filepath: ", self.save_location)
        # self.twitter_archive.set_save_path(self.save_location)

    def open_file_webarchive(self):
        name = tk.filedialog.askopenfilename(initialdir=os.getcwd(),
                                             filetypes=(("Text File", "*.txt"), ("All Files", "*.*")),
                                             title="Choose a file."
                                             )
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            webarchive_urls = open(name, 'r')
            print("webarchive_urls", webarchive_urls)
            print("Length of Links Before Open File: ", len(self.url_list_twitter_archive))
            for url in webarchive_urls:
                self.url_list_twitter_archive.append(url)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_twitter_archive = len(self.url_list_twitter_archive)
            self.twitter_percentage_text.set((
                f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
                f"{(self.progress_bar_value_twitter_archive / self.progress_bar_max_value_twitter_archive) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_twitter_archive} videos from file: {name}')
        except Exception as e:
            print("No file exists: ", e)
            self.status.set(f'File Not Found')

    def refresh_webarchive_list(self):
        self.twitter_url_listbox.delete(0, tk.END)
        self.url_list_twitter_archive = list(dict.fromkeys(self.url_list_twitter_archive))
        for items in self.url_list_twitter_archive:
            self.twitter_url_listbox.insert(tk.END, items)

    def add_webarchive_url(self):
        # Get Web Links
        parse_addition = self.twitter_url_entry.get("1.0", tk.END)
        if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', parse_addition) != "":
            parse_addition_array = parse_addition.splitlines()
            for url in parse_addition_array:
                if re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url) != "":
                    self.status.set(f'Added URLs to Queue')
                    temp = re.sub(r'[^A-Za-z0-9_./:&?!=-]', '', url)
                    self.url_list_twitter_archive.append(temp)
                else:
                    print("Bad URL: ", url)
                    self.status.set(f'Paste Some Website Links First! (CTRL+V) {url}')
            self.url_list_twitter_archive = list(dict.fromkeys(self.url_list_twitter_archive))
            self.twitter_url_entry.delete("1.0", tk.END)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_twitter_archive = len(self.url_list_twitter_archive)
            print((
                f'URL: {self.url_list_twitter_archive} AND AND MAXVAL: {self.progress_bar_max_value_twitter_archive} AND LEN: '
                f' {len(self.url_list_twitter_archive)}'))
            self.twitter_percentage_text.set((
                f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
                f"{(self.progress_bar_value_twitter_archive / self.progress_bar_max_value_twitter_archive) * 100}%"))
            self.status.set(f'Queued {self.progress_bar_max_value_twitter_archive} url(s)')

    def remove_webarchive_url(self):
        if self.twitter_url_listbox.curselection():
            selected_text_list = [self.twitter_url_listbox.get(i) for i in self.twitter_url_listbox.curselection()]
            x = 0
            for url in selected_text_list:
                self.url_list_twitter_archive.remove(url)
                x += 1
            self.refresh_webarchive_list()
            self.progress_bar_max_value_twitter_archive = len(self.url_list_twitter_archive)
            if self.progress_bar_max_value_twitter_archive == 0:
                self.twitter_percentage_text.set(
                    f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | {0 * 100}%")
                self.progress_bar_twitter_archive['value'] = 0
                self.progress_bar_value_twitter_archive = 0
            else:
                self.twitter_percentage_text.set((
                    f"{self.progress_bar_value_twitter_archive}/{self.progress_bar_max_value_twitter_archive} | ",
                    f"{(self.progress_bar_value_twitter_archive / self.progress_bar_max_value_twitter_archive) * 100}%"))
                self.progress_bar_twitter_archive['value'] = self.progress_bar_max_value_twitter_archive
                self.progress_bar_twitter_archive['maximum'] = self.progress_bar_max_value_twitter_archive
                self.progress_bar_value_twitter_archive = self.progress_bar_max_value_twitter_archive
            self.status.set(f'Queued {self.progress_bar_max_value_twitter_archive} videos')
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"


# Media Converter Class
class MediaConverterFrame(tk.Frame):
    url_list_web_archive = []
    web_archive = None
    log = None
    tabControl = None
    web_archive_frame = None
    status = None
    save_location = None

    def __init__(self, tkt_main, tab_control, status, logger=None):
        if logger:
            self.log = logger
        else:
            self.log = Log()
        self.tkt = tkt_main
        self.tabControl = tab_control
        self.status = status
        self.web_archive = WebPageArchive(self.log)
        self.draw_frame()
        self.tabControl.add(self.web_archive_frame, text="Media Converter")
        tk.Frame.__init__(self, self.web_archive_frame)  # , bg="red")

    @staticmethod
    def run(func, name=None):
        threading.Thread(target=func, name=name).start()

    def draw_frame(self):
        self.web_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.web_archive_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.web_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.web_archive_frame, 1, minsize=1, weight=1)
        web_archive_selection_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(web_archive_selection_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(web_archive_selection_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(web_archive_selection_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(web_archive_selection_frame, 0, minsize=1, weight=1)
        web_archive_config_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(web_archive_config_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(web_archive_config_frame, 0, minsize=1, weight=0)
        top_web_frame = ttk.Frame(web_archive_selection_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(top_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_web_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(top_web_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(top_web_frame, 0, minsize=1, weight=1)
        middle_web_button_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(middle_web_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(middle_web_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_button_frame, 3, minsize=1, weight=1)
        middle_web_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(middle_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(middle_web_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(middle_web_frame, 0, minsize=1, weight=1)
        bottom_web_frame = ttk.Frame(web_archive_selection_frame)
        tk.Grid.rowconfigure(bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(bottom_web_frame, 1, minsize=1, weight=1)

    # This class handles [TAB] Key to move to next Widget
    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"


# Call Main Function
def main():
    if __name__ == "__main__":
        root = tk.Tk()
        tkthread = tkt.TkThread(root)  # make the thread-safe callable
        GeniusBot(root, tkthread)
        root.mainloop()


main()
