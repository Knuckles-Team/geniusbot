# from tkinter.filedialog import askopenfilename, askdirectory
import threading
import tkinter as tk
from tkinter import ttk, filedialog, font

import tkthread as tkt  # TkThread

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from youtube_download import YouTubeDownloader
from webpage_archive import WebPageArchive
from version_info import geniusbot_version
from log import Log

# Implement the default Matplotlib key bindings.
'''from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure'''
# import queue
import re
import os
import pyglet
import requests
from PIL import ImageTk, Image


class GeniusBot:
    hex_color_background = '#3E4A57'
    progress_bar_youtube = None
    progress_bar_value_youtube = 0
    progress_bar_max_value_youtube = 0
    progress_bar_webarchive = None
    progress_bar_value_webarchive = 0
    progress_bar_max_value_webarchive = 0
    # w_text = None
    tkt = None
    url_list_youtube = []
    url_list_webarchive = []
    root = None
    youtube_downloader = None
    web_archiver = None
    save_location = os.getcwd()
    style = None
    font = None
    tabControl = None
    version = geniusbot_version
    log = None

    def __init__(self, root_main, tkt_main):
        self.log = Log()
        self.root = root_main
        self.tkt = tkt_main
        self.init_font()
        self.init_icon()
        # self.root.geometry("500x700")
        # self.root.minsize(500, 700)
        self.init_styles()
        self.init_main_frame()
        self.log.info("Initializing GeniusBot Complete!")
        self.youtube_downloader = YouTubeDownloader(self.log)
        self.web_archiver = WebPageArchive(self.log)


    def init_font(self):
        self.fontpath = f'{os.pardir}/fonts/OpenSans/OpenSans-Regular.ttf'
        self.fontpath_alt = f'{os.curdir}/fonts/OpenSans/OpenSans-Regular.ttf'
        if os.path.isfile(self.fontpath):
            pyglet.font.add_file(self.fontpath)
            action_man = pyglet.font.load('OpenSans')
            self.font = tk.font.Font(family="OpenSans", size=10)
            # self.font = tk.font.Font(family="Times New Roman", size=12)
            print("Using Open_Sans")
        elif os.path.isfile(self.fontpath_alt):
            pyglet.font.add_file(self.fontpath_alt)
            action_man = pyglet.font.load('OpenSans')
            self.font = tk.font.Font(family="OpenSans", size=10)
            # self.font = tk.font.Font(family="Times New Roman", size=12)
            print("Using Open_Sans")
        else:
            print("Using Times new Roman")
            self.font = tk.font.Font(family="Times New Roman", size=10)

    def init_icon(self):
        self.iconpath = f'{os.pardir}/img/geniusbot.ico'
        if os.path.isfile(self.iconpath):
            print("Icon Found")
        else:
            self.iconpath = f'{os.curdir}/img/geniusbot.ico'
        print(self.iconpath)
        # self.root.wm_iconbitmap(os.path.abspath(self.iconpath))
        try:
            self.root.iconbitmap(os.path.abspath(self.iconpath))
        except tk.TclError:
            print("Icon not found")
            try:
                self.root.wm_iconbitmap(os.path.abspath(self.iconpath))
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
        # Frame UI
        tk.Grid.rowconfigure(self.root, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.root, 0, minsize=1, weight=1)
        self.main_frame = ttk.Frame(self.root)
        tk.Grid.rowconfigure(self.main_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.main_frame, 1, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.main_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.main_frame, 0, minsize=1, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='NSEW')
        self.title = tk.StringVar()
        self.title.set("GeniusBot")
        self.title_frame = ttk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.title_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.title_frame, 0, minsize=1, weight=1)
        self.title_label = ttk.Label(self.title_frame, textvariable=self.title, style="Title.TLabel")
        self.tabControl = ttk.Notebook(self.main_frame)
        self.notification_frame = ttk.Frame(self.main_frame)
        # self.home_tab = tk.Frame(self.tabControl)
        # self.web_archive = tk.Frame(self.tabControl)
        self.report_merger_tab = tk.Frame(self.tabControl)
        self.analytical_profiler = tk.Frame(self.tabControl)
        self.title_frame.grid(row=0, column=0, sticky='NSEW')
        self.notification_frame.grid(row=5, column=0, sticky='NSEW')
        # Sets up Status Bar
        self.status = tk.StringVar()
        self.status.set(f"Welcome {os.getlogin()}! Please navigate to a tab to begin using GeniusBot!")
        self.status_label = tk.Label(self.notification_frame, bg=self.hex_color_background, fg="white", bd=1,
                                     textvariable=self.status, anchor='w', relief=tk.SUNKEN)
        self.status_label.grid(column=0, row=0, sticky='NSEW', columnspan=1)
        self.init_home_frame()
        self.init_youtube_frame()
        self.init_web_archive_frame()
        self.tabControl.add(self.home_frame, text="Home")
        self.tabControl.add(self.youtube_archive_frame, text="YouTube Archive")
        self.tabControl.add(self.web_archive_frame, text="Web Archive")
        # self.tabControl.add(self.report_merger_tab, text="Report Merger")
        # self.tabControl.add(self.analytical_profiler, text="Analytical Profiler")
        self.tabControl.grid(column=0, row=1, sticky='NSEW')

    def init_home_frame(self):
        self.home_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.home_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.home_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.home_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.home_frame, 0, minsize=1, weight=1)
        self.top_frame_home = ttk.Frame(self.home_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(self.top_frame_home, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame_home, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame_home, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.top_frame_home, 0, minsize=1, weight=1)
        self.home_title = tk.StringVar()
        self.home_title.set(
            f"""GeniusBot is a world class tool that allows you to do a lot of useful\n
            things from a compact and portable application\n
            1. YouTube Archive\n
            2. Web Archive\n
            3. FFMPEG Video/Audio Converter (Coming Soon)\n
            4. Analytical Profiler (Coming Soon)\n
            5. Report Merger (Coming Soon)\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
            """)
        self.home_title_label = ttk.Label(self.top_frame_home, textvariable=self.home_title, anchor='w', style="Notes"
                                                                                                               ".TLabel")
        self.top_frame_home.grid(row=1, column=0, sticky='NSEW')
        self.home_title_label.grid(column=0, row=0, columnspan=3)

    def init_youtube_frame(self):
        self.youtube_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.youtube_archive_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.youtube_archive_frame, 0, minsize=1, weight=1)
        self.top_frame = ttk.Frame(self.youtube_archive_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(self.top_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.top_frame, 0, minsize=1, weight=1)
        self.middle_button_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(self.middle_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.middle_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_button_frame, 3, minsize=1, weight=1)
        self.middle_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(self.middle_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.middle_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_frame, 0, minsize=1, weight=1)
        self.bottom_frame = ttk.Frame(self.youtube_archive_frame)
        tk.Grid.rowconfigure(self.bottom_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.bottom_frame, 1, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.bottom_frame, 2, minsize=1, weight=1)

        tk.Grid.rowconfigure(self.notification_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.notification_frame, 0, minsize=1, weight=1)

        # Buttons
        self.add_url_button = ttk.Button(self.middle_button_frame, text="Add", style='Add.TButton', width=12,
                                         command=self.add_youtube_url)
        self.add_url_button.grid(column=0, row=1, sticky='NSEW', padx=5, pady=10)
        self.remove_url_button = ttk.Button(self.middle_button_frame, text="Remove", style='Remove.TButton', width=12,
                                            command=self.remove_youtube_url)
        self.remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=5, pady=10)
        self.openfile_button = ttk.Button(self.middle_button_frame, text="Open File", style='Open.TButton', width=12,
                                          command=self.open_file_youtube)
        self.openfile_button.grid(column=2, row=1, sticky='NSEW', padx=5, pady=10)
        self.save_location_button = ttk.Button(self.middle_button_frame, text="Save Location", width=18,
                                               command=self.choose_save_location_youtube)

        self.save_location_button.grid(column=3, row=1, sticky='NSEW', padx=5, pady=10)

        self.file_type = tk.StringVar()
        self.file_type.set("Video")
        self.file_type_menu = tk.OptionMenu(self.bottom_frame, self.file_type, "Video", "Audio",
                                            command=self.set_file_type)
        self.video_quality_type = tk.StringVar()
        self.video_quality_type.set("Highest")
        self.video_quality_type_menu = tk.OptionMenu(self.bottom_frame, self.video_quality_type, "Highest", "720p",
                                                     "Lowest")
        self.audio_quality_type = tk.StringVar()
        self.audio_quality_type.set("320kbps")
        self.audio_quality_type_menu = tk.OptionMenu(self.bottom_frame, self.audio_quality_type, "320kbps", "256kbps",
                                                     "128kbps")

        self.file_type_menu.grid(column=0, row=3, sticky='NSEW', padx=5, pady=10)
        self.video_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
        # self.audio_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)
        # self.audio_quality_type_menu.grid_forget()
        # self.download_button_video = ttk.Button(self.bottom_frame, text="Download Video", command=lambda: self.run(lambda: self.download_video(), name='NoSync'))
        # self.download_button_video.grid(column=0, row=3, sticky='NSEW', padx=5, pady=10)
        self.download_button = ttk.Button(self.bottom_frame, text="Download",
                                          command=lambda: self.run(lambda: self.youtube_download(), name='NoSync'))
        self.download_button.grid(column=2, row=3, sticky='NSEW', padx=15, pady=10)

        # Labels
        # self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.queue_title = tk.StringVar()
        self.queue_title.set("Download Queue")
        self.queue_title_label = ttk.Label(self.middle_frame, textvariable=self.queue_title, style="Notes.TLabel")
        self.queue_title_label.grid(column=0, row=0, columnspan=3)
        self.youutube_links_text = tk.StringVar()
        self.youutube_links_text.set(r'Enter YouTube Link(s) ⮟')
        self.youutube_links_label = ttk.Label(self.top_frame, textvariable=self.youutube_links_text,
                                              style="Notes.TLabel")
        self.youutube_links_label.grid(column=0, row=0, columnspan=2, sticky='W')
        self.youutube_channels_text = tk.StringVar()
        self.youutube_channels_text.set(r'Enter YouTube Channel or User ⮞')
        self.youutube_channels_label = ttk.Label(self.top_frame, textvariable=self.youutube_channels_text,
                                                 style="Notes.TLabel")
        self.youutube_channels_label.grid(column=0, row=4, columnspan=2, sticky='W')
        self.youtube_percentage_text = tk.StringVar()
        self.youtube_percentage_text.set(
            f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / (self.progress_bar_max_value_youtube + 1)) * 100}%")
        self.percentage_label = ttk.Label(self.bottom_frame, textvariable=self.youtube_percentage_text, style="Notes.TLabel")
        self.percentage_label.grid(column=0, row=2, columnspan=3)
        self.percentage_title = tk.StringVar()
        self.percentage_title.set("Percentage")
        self.percentage_title_label = ttk.Label(self.bottom_frame, textvariable=self.percentage_title,
                                                style="Notes.TLabel")
        self.percentage_title_label.grid(column=0, row=0, columnspan=3)

        # ListBox
        self.url_listbox = tk.Listbox(self.middle_frame, height=12, selectmode='multiple', exportselection=0)
        self.url_listbox.grid(column=0, row=1, columnspan=3, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.url_listbox, 0, weight=1)

        # Entries
        self.url_entry = tk.Text(self.top_frame, height=9)
        self.channel_entry = tk.Text(self.top_frame, height=1, width=33)
        # tk.Grid.columnconfigure(self.url_entry, 0, weight=1)
        self.channel_entry.bind("<Tab>", self.focus_next_widget)
        self.channel_entry.grid(column=1, row=4, columnspan=2, stick='NSEW')
        self.url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_youtube_list()
        self.url_entry.grid(column=0, row=2, columnspan=3, sticky='NSEW')

        # Progress Bar
        self.progress_bar_youtube = ttk.Progressbar(
            self.bottom_frame, orient="horizontal",
            length=300, mode="determinate"
        )
        self.progress_bar_youtube.grid(column=0, row=1, padx=15, pady=10, columnspan=3, sticky='NSEW')
        self.top_frame.grid(row=1, column=0, sticky='NSEW')
        self.middle_button_frame.grid(row=2, column=0, sticky='NSEW')
        self.middle_frame.grid(row=3, column=0, sticky='NSEW')
        self.bottom_frame.grid(row=4, column=0, sticky='NSEW')
        self.title_label.grid(column=0, row=0, sticky='NSEW', columnspan=1, padx=10, pady=10)

    def init_web_archive_frame(self):
        self.web_archive_frame = tk.Frame(self.tabControl)
        tk.Grid.rowconfigure(self.web_archive_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.web_archive_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.web_archive_frame, 1, minsize=1, weight=1)
        self.web_archive_selection_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 2, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 3, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 4, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.web_archive_selection_frame, 5, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.web_archive_selection_frame, 0, minsize=1, weight=1)
        self.web_archive_config_frame = ttk.Frame(self.web_archive_frame)
        tk.Grid.rowconfigure(self.web_archive_config_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.web_archive_config_frame, 0, minsize=1, weight=0)
        self.top_web_frame = ttk.Frame(self.web_archive_selection_frame)
        # self.tabControl.pack(expand=1, fill="both")
        tk.Grid.rowconfigure(self.top_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_web_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_web_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.top_web_frame, 0, minsize=1, weight=1)
        self.middle_web_button_frame = ttk.Frame(self.web_archive_selection_frame)
        tk.Grid.rowconfigure(self.middle_web_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.middle_web_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_web_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_web_button_frame, 2, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_web_button_frame, 3, minsize=1, weight=1)
        self.middle_web_frame = ttk.Frame(self.web_archive_selection_frame)
        tk.Grid.rowconfigure(self.middle_web_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.middle_web_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_web_frame, 0, minsize=1, weight=1)
        self.bottom_web_frame = ttk.Frame(self.web_archive_selection_frame)
        tk.Grid.rowconfigure(self.bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_web_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_web_frame, 1, minsize=1, weight=1)

        tk.Grid.rowconfigure(self.notification_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.notification_frame, 0, minsize=1, weight=1)
        # Buttons
        self.web_add_url_button = ttk.Button(self.middle_web_button_frame, text="Add", style='Add.TButton', width=9,
                                             command=self.add_webarchive_url)
        self.web_add_url_button.grid(column=0, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_remove_url_button = ttk.Button(self.middle_web_button_frame, text="Remove", style='Remove.TButton',
                                                width=9, command=self.remove_webarchive_url)
        self.web_remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_openfile_button = ttk.Button(self.middle_web_button_frame, text="Open File", style='Open.TButton',
                                              width=9, command=self.open_file_webarchive)
        self.web_openfile_button.grid(column=2, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_save_location_button = ttk.Button(self.middle_web_button_frame, text="Save Location", width=15,
                                                   command=self.choose_save_location_webarchive)
        self.web_save_location_button.grid(column=3, row=1, sticky='NSEW', padx=5, pady=10)
        self.web_archive_button = ttk.Button(self.bottom_web_frame, text="Begin Archive",
                                             command=lambda: self.run(lambda: self.archive_sites(), name='NoSync'))
        self.web_archive_button.grid(column=0, row=3, columnspan=2, sticky='NSEW', padx=15, pady=10)

        # Labels
        # self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.web_queue_title = tk.StringVar()
        self.web_queue_title.set("Download Queue")
        self.web_queue_title_label = ttk.Label(self.middle_web_frame,
                                               textvariable=self.web_queue_title,
                                               style="Notes.TLabel")
        self.web_queue_title_label.grid(column=0, row=0, columnspan=1)
        self.web_config_title = tk.StringVar()
        self.web_config_title.set("Configure Archive")
        self.web_config_title_label = ttk.Label(self.web_archive_config_frame, textvariable=self.web_config_title,
                                                style="Notes.TLabel")
        self.web_config_title_label.grid(column=0, row=0, columnspan=2, pady=(5, 5), sticky='NSEW')
        self.web_config_screenshot_value = tk.IntVar()
        self.web_config_screenshot_value.set(1)
        self.web_config_screenshot = ttk.Checkbutton(self.web_archive_config_frame, text="Capture Screenshot",
                                                     variable=self.web_config_screenshot_value, onvalue=1, offvalue=0,
                                                     style="TCheckbutton", command=self.onclick_capture_screenshot)
        self.web_config_screenshot.grid(column=0, row=1, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_filetype_title = ttk.Label(self.web_archive_config_frame, text="File Type",
                                                       style="Notes.TLabel")
        self.web_screenshot_filetype_title.grid(column=0, row=2, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_filetype = tk.StringVar()
        self.web_screenshot_filetype.set("PNG")  # default value
        self.web_screenshot_filetype_menu = ttk.OptionMenu(self.web_archive_config_frame, self.web_screenshot_filetype,
                                                           "PNG", "PNG", "JPEG")
        self.web_screenshot_filetype_menu.grid(column=1, row=2, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_size_title = ttk.Label(self.web_archive_config_frame, text="Size",
                                                   style="Notes.TLabel")
        self.web_screenshot_size_title.grid(column=0, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_size = tk.StringVar()
        self.web_screenshot_size.set("Full")  # default value
        self.web_screenshot_size_menu = ttk.OptionMenu(self.web_archive_config_frame, self.web_screenshot_size,
                                                       "Full", "Full", "Normal")
        self.web_screenshot_size_menu.grid(column=1, row=3, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_quality_title = ttk.Label(self.web_archive_config_frame, text="Quality",
                                                      style="Notes.TLabel")
        self.web_screenshot_quality_title.grid(column=0, row=4, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_screenshot_quality_value = tk.IntVar()
        self.web_screenshot_quality_value.set(100)
        self.web_screenshot_quality = tk.Scale(self.web_archive_config_frame, from_=10, to=100,
                                               variable=self.web_screenshot_quality_value, orient=tk.HORIZONTAL)
        self.web_screenshot_quality.grid(column=1, row=4, columnspan=1, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_htmldl_value = tk.IntVar()
        self.web_config_htmldl = ttk.Checkbutton(self.web_archive_config_frame, text="Archive Website",
                                                 variable=self.web_config_htmldl_value, onvalue=1, offvalue=0,
                                                 style="TCheckbutton")
        self.web_config_htmldl.grid(column=0, row=5, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_compress_value = tk.IntVar()
        self.web_config_compress = ttk.Checkbutton(self.web_archive_config_frame, text="Compress/Zip",
                                                   variable=self.web_config_compress_value, onvalue=1, offvalue=0,
                                                   style="TCheckbutton")
        self.web_config_compress.grid(column=0, row=6, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_config_twitter_value = tk.IntVar()
        self.web_config_twitter = ttk.Checkbutton(self.web_archive_config_frame, text="Twitter to CSV",
                                                  variable=self.web_config_twitter_value, onvalue=1, offvalue=0,
                                                  style="TCheckbutton")
        self.web_config_twitter.grid(column=0, row=7, columnspan=2, padx=(5, 5), pady=(5, 5), sticky='NSEW')
        self.web_links_text = tk.StringVar()
        self.web_links_text.set(r'Enter Web Link(s) ⮟')
        self.web_links_label = ttk.Label(self.top_web_frame, textvariable=self.web_links_text, style="Notes.TLabel")
        self.web_links_label.grid(column=0, row=0, columnspan=1, sticky='W')
        self.web_percentage_text = tk.StringVar()
        self.web_percentage_text.set(
            f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / (self.progress_bar_max_value_webarchive + 1)) * 100}%")
        self.web_percentage_label = ttk.Label(self.bottom_web_frame, textvariable=self.web_percentage_text,
                                              style="Notes.TLabel")
        self.web_percentage_label.grid(column=0, row=2, columnspan=2)
        self.web_percentage_title = tk.StringVar()
        self.web_percentage_title.set("Percentage")
        self.web_percentage_title_label = ttk.Label(self.bottom_web_frame, textvariable=self.web_percentage_title,
                                                    style="Notes.TLabel")
        self.web_percentage_title_label.grid(column=0, row=0, columnspan=2)

        # ListBox
        self.web_url_listbox = tk.Listbox(self.middle_web_frame, height=12)
        self.web_url_listbox.grid(column=0, row=1, columnspan=2, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.url_listbox, 0, weight=1)

        # Entries
        self.web_url_entry = tk.Text(self.top_web_frame, height=9)
        self.web_url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_webarchive_list()
        self.web_url_entry.grid(column=0, row=2, columnspan=2, sticky='NSEW')

        # Progress Bar
        self.progress_bar_webarchive = ttk.Progressbar(
            self.bottom_web_frame, orient="horizontal",
            mode="determinate"
        )
        self.web_archive_selection_frame.grid(column=1, row=0, columnspan=1, sticky='NSEW')
        self.web_archive_config_frame.grid(column=0, row=0, columnspan=1, sticky='NSEW')
        self.progress_bar_webarchive.grid(column=0, row=1, padx=15, pady=10, columnspan=2, sticky='NSEW')
        self.top_web_frame.grid(row=1, column=0, sticky='NSEW')
        self.middle_web_button_frame.grid(row=2, column=0, sticky='NSEW')
        self.middle_web_frame.grid(row=3, column=0, sticky='NSEW')
        self.bottom_web_frame.grid(row=4, column=0, sticky='NSEW')
        # self.title_label.grid(column=0, row=0, sticky='NSEW', columnspan=1, padx=10, pady=10)

    def run(self, func, name=None):
        threading.Thread(target=func, name=name).start()

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
        elif self.file_type.get() == "Audio":
            self.video_quality_type_menu.grid_forget()
            self.audio_quality_type_menu.grid(column=1, row=3, sticky='NSEW', padx=5, pady=10)

    # This class handles [TAB] Key to move to next Widget
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return ("break")

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
            self.youtube_percentage_text.set(
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos from file: {name}')
        except:
            print("No file exists")
            self.status.set(f'File Not Found')

    def refresh_youtube_list(self):
        self.url_listbox.delete(0, tk.END)
        self.url_list_youtube = list(dict.fromkeys(self.url_list_youtube))
        for items in self.url_list_youtube:
            self.url_listbox.insert(tk.END, items)

    def add_youtube_url(self):
        # Get Channel
        parse_channel_addition = ""
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
            self.youtube_percentage_text.set(
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
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
            self.youtube_percentage_text.set(
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
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
                    f"{self.progress_bar_max_value_youtube}/{self.progress_bar_max_value_youtube} | {(0) * 100}%")
                self.progress_bar_youtube['value'] = 0
                self.progress_bar_value_youtube = 0
            else:
                self.youtube_percentage_text.set(
                    f"{self.progress_bar_max_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
                self.progress_bar_youtube['value'] = self.progress_bar_max_value_youtube
                self.progress_bar_value_youtube = self.progress_bar_max_value_youtube
            self.status.set(f'Queued {self.progress_bar_max_value_youtube} videos')
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    def choose_save_location_webarchive(self):
        self.save_location = tk.filedialog.askdirectory()
        print("Save Filepath: ", self.save_location)
        self.web_archiver.set_save_path(self.save_location)

    def open_file_webarchive(self):
        name = tk.filedialog.askopenfilename(initialdir=os.getcwd(),
                                             filetypes=(("Text File", "*.txt"), ("All Files", "*.*")),
                                             title="Choose a file."
                                             )
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            webarchive_urls = open(name, 'r')
            print("webarchive_urls", webarchive_urls)
            print("Length of Links Before Open File: ", len(self.url_list_webarchive))
            for url in webarchive_urls:
                self.url_list_webarchive.append(url)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_webarchive = len(self.url_list_webarchive)
            self.web_percentage_text.set(
                f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / self.progress_bar_max_value_webarchive) * 100}%")
            self.status.set(f'Queued {self.progress_bar_max_value_webarchive} videos from file: {name}')
        except:
            print("No file exists")
            self.status.set(f'File Not Found')

    def refresh_webarchive_list(self):
        self.web_url_listbox.delete(0, tk.END)
        self.url_list_webarchive = list(dict.fromkeys(self.url_list_webarchive))
        for items in self.url_list_webarchive:
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
                    self.url_list_webarchive.append(temp)
                else:
                    print("Bad URL: ", url)
                    self.status.set(f'Paste Some Website Links First! (CTRL+V) {url}')
            self.url_list_webarchive = list(dict.fromkeys(self.url_list_webarchive))
            self.web_url_entry.delete("1.0", tk.END)
            self.refresh_webarchive_list()
            self.progress_bar_max_value_webarchive = len(self.url_list_webarchive)
            print(
                f'URL: {self.url_list_webarchive} AND AND MAXVAL: {self.progress_bar_max_value_webarchive} AND LEN {len(self.url_list_webarchive)}')
            self.web_percentage_text.set(
                f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / self.progress_bar_max_value_webarchive) * 100}%")
            self.status.set(f'Queued {self.progress_bar_max_value_webarchive} url(s)')

    def remove_webarchive_url(self):
        if self.web_url_listbox.curselection():
            selected_text_list = [self.web_url_listbox.get(i) for i in self.web_url_listbox.curselection()]
            x = 0
            for url in selected_text_list:
                self.url_list_webarchive.remove(url)
                x += 1
            self.refresh_webarchive_list()
            self.progress_bar_max_value_webarchive = len(self.url_list_webarchive)
            if self.progress_bar_max_value_webarchive == 0:
                self.web_percentage_text.set(
                    f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(0) * 100}%")
                self.progress_bar_webarchive['value'] = 0
                self.progress_bar_value_webarchive = 0
            else:
                self.web_percentage_text.set(
                    f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / self.progress_bar_max_value_webarchive) * 100}%")
                self.progress_bar_webarchive['value'] = self.progress_bar_max_value_webarchive
                self.progress_bar_value_webarchive = self.progress_bar_max_value_webarchive
            self.status.set(f'Queued {self.progress_bar_max_value_webarchive} videos')
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    def archive_sites(self):
        self.url_list_webarchive = list(filter(None, self.url_list_webarchive))
        self.url_list_webarchive = list(dict.fromkeys(self.url_list_webarchive))
        self.progress_bar_max_value_webarchive = len(self.url_list_webarchive)
        if self.progress_bar_max_value_webarchive > 0:
            self.status.set(f'Downloading {len(self.url_list_webarchive)} URL(s)')
            self.web_archive_button["state"] = "disabled"
            self.web_add_url_button["state"] = "disabled"
            self.web_remove_url_button["state"] = "disabled"
            self.web_openfile_button["state"] = "disabled"
            self.web_save_location_button["state"] = "disabled"
            self.progress_bar_value_webarchive = 0
            self.progress_bar_webarchive['maximum'] = self.progress_bar_max_value_webarchive
            self.progress_bar_webarchive['value'] = 0
            print(f'{self.progress_bar_max_value_webarchive}:MAX VALUE')
            self.web_percentage_text.set(
                f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / self.progress_bar_max_value_webarchive) * 100}%")
            # Check to see if screenshot capture is enabled to launch browser
            if self.web_config_screenshot_value.get() == 1:
                self.web_archiver.launch_browser()
            i = 0
            for url in self.url_list_webarchive:
                self.web_archiver.append_link(url=url)
                print("Links Sent: ", self.web_archiver.get_links())
                # Check to see if screenshot capture is enabled to capture screenshot
                if self.web_config_screenshot_value.get() == 1:
                    if self.web_screenshot_size.get() == "Full":
                        self.web_archiver.fullpage_screenshot(url=url,
                                                              filetype=self.web_screenshot_filetype.get(),
                                                              quality=self.web_screenshot_quality.get())
                    elif self.web_screenshot_size.get() == "Normal":
                        self.web_archiver.screenshot(url=url,
                                                     filetype=self.web_screenshot_filetype.get(),
                                                     quality=self.web_screenshot_quality.get())
                # self.youtube_downloader.download_hd_videos()
                self.web_archiver.reset_links()
                self.progress_bar_value_webarchive = i + 1
                self.web_percentage_text.set(
                    f"{self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive} | {(self.progress_bar_value_webarchive / self.progress_bar_max_value_webarchive) * 100}%")
                self.progress_bar_webarchive['value'] = i + 1
                print("Value: ", self.progress_bar_value_webarchive)
                print("Max Value: ", self.progress_bar_max_value_webarchive)
                self.status.set(
                    f'Completed {self.progress_bar_value_webarchive}/{self.progress_bar_max_value_webarchive}')
                i += 1
            # Check to see if screenshot capture is enabled to quit browser
            if self.web_config_screenshot_value.get() == 1:
                self.web_archiver.quit_driver()
            self.tabControl.tab(1, state="normal")
            self.tabControl.tab(2, state="normal")
            self.web_archive_button["state"] = "enabled"
            self.web_add_url_button["state"] = "enabled"
            self.web_remove_url_button["state"] = "enabled"
            self.web_openfile_button["state"] = "enabled"
            self.web_save_location_button["state"] = "enabled"
            self.status.set(f'Downloaded {self.progress_bar_value_webarchive} website screenshot(s)!')
        else:
            print("No Website Links Added")
            self.status.set(f'Add Some Website Links First!')

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
            self.youtube_percentage_text.set(
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
            i = 0
            for url in self.url_list_youtube:
                self.youtube_downloader.append_link(url)
                print("Links Sent: ", self.youtube_downloader.get_link())
                self.youtube_downloader.download_videos(quality)
                self.youtube_downloader.reset_links()
                self.progress_bar_value_youtube = i + 1
                self.youtube_percentage_text.set(
                    f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
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
            self.youtube_percentage_text.set(
                f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
            i = 0
            for url in self.url_list_youtube:
                self.youtube_downloader.append_link(url)
                self.youtube_downloader.download_audio(quality=quality)
                self.youtube_downloader.reset_links()
                self.progress_bar_value_youtube = i + 1
                self.youtube_percentage_text.set(
                    f"{self.progress_bar_value_youtube}/{self.progress_bar_max_value_youtube} | {(self.progress_bar_value_youtube / self.progress_bar_max_value_youtube) * 100}%")
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


root = tk.Tk()
root.minsize(width=500, height=700)
root.title("GeniusBot")
root.geometry("500x700")
root.minsize(500, 700)
# root.maxsize(width=600, height=800)
tkthread = tkt.TkThread(root)  # make the thread-safe callable
main_ui = GeniusBot(root, tkthread)
root.mainloop()
