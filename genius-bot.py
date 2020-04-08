import time
from tkinter.filedialog import askopenfilename
from tkthread import tk, TkThread
from tkinter import ttk
import tkinter as tk
import threading
import time
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from youtube_download import YouTubeDownloader
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
import queue
import re
import os


class GeniusBot:
    progress_bar = None
    value = 0
    max_value = 0
    w_text = None
    tkt = None
    url_list = []
    root = None
    youtube_downloader = None

    def __init__(self, root_main, tkt_main):
        self.youtube_downloader = YouTubeDownloader()
        self.root = root_main
        self.tkt = tkt_main
        # Frame UI
        tk.Grid.rowconfigure(self.root, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.root, 0, minsize=1, weight=1)
        self.main_frame = tk.Frame(self.root)
        tk.Grid.rowconfigure(self.main_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.main_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.main_frame, 2, minsize=1, weight=1)
        tk.Grid.rowconfigure(self.main_frame, 3, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.main_frame, 4, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.main_frame, 0, minsize=1, weight=1)
        self.top_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.top_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame, 1, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.top_frame, 2, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.top_frame, 0, minsize=1, weight=1)
        self.middle_button_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.middle_button_frame, 0, minsize=1, weight=0)
        tk.Grid.columnconfigure(self.middle_button_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_button_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_button_frame, 2, minsize=1, weight=1)
        self.middle_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.middle_frame, 0, minsize=1, weight=0)
        tk.Grid.rowconfigure(self.middle_frame, 1, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.middle_frame, 0, minsize=1, weight=1)
        self.bottom_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.bottom_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_frame, 1, minsize=1, weight=1)
        self.notification_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.notification_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.notification_frame, 0, minsize=1, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='NSEW')
        self.top_frame.grid(row=0, column=0, sticky='NSEW')
        self.middle_button_frame.grid(row=1, column=0, sticky='NSEW')
        self.middle_frame.grid(row=2, column=0, sticky='NSEW')
        self.bottom_frame.grid(row=3, column=0, sticky='NSEW')
        self.notification_frame.grid(row=4, column=0, sticky='NSEW')

        # Buttons
        self.add_url_button = ttk.Button(self.middle_button_frame, text="Add", command=self.add_url)
        self.add_url_button.grid(column=0, row=0, sticky='NSEW', padx=15, pady=10)
        self.remove_url_button = ttk.Button(self.middle_button_frame, text="Remove", command=self.remove_url)
        self.remove_url_button.grid(column=1, row=0, sticky='NSEW', padx=15, pady=10)
        self.openfile_button = ttk.Button(self.middle_button_frame, text="Open File", command=self.open_file)
        self.openfile_button.grid(column=2, row=0, sticky='NSEW', padx=15, pady=10)
        self.download_button_video = ttk.Button(self.bottom_frame, text="Download Video", command=self.download_videos)
        self.download_button_video.grid(column=0, row=3, sticky='NSEW', padx=15, pady=10)
        self.download_button_audio = ttk.Button(self.bottom_frame, text="Download Audio", command=self.download_audios)
        self.download_button_audio.grid(column=1, row=3, sticky='NSEW', padx=15, pady=10)

        # Labels
        self.title = tk.StringVar()
        self.title.set("Genius - Web Archive")
        self.title_label = tk.Label(self.top_frame, textvariable=self.title)
        self.title_label.grid(column=0, row=0, sticky='NSEW', columnspan=1)
        self.status = tk.StringVar()
        self.status.set("Welcome - Please begin by entering YouTube URLs")
        self.status_label = tk.Label(self.notification_frame, bd=1, textvariable=self.status, anchor='w', relief=tk.SUNKEN)
        self.status_label.grid(column=0, row=0, sticky='NSEW', columnspan=1)
        #self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.queue_title = tk.StringVar()
        self.queue_title.set("Video Download Queue")
        self.queue_title_label = tk.Label(self.middle_frame, textvariable=self.queue_title)
        self.queue_title_label.grid(column=0, row=0, columnspan=3)
        self.w_text = tk.StringVar()
        self.w_text.set("Enter YouTube Link(s) Below: ")
        self.w = tk.Label(self.top_frame, textvariable=self.w_text)
        self.w.grid(column=0, row=1, columnspan=2, sticky='W')
        self.percentage_text = tk.StringVar()
        self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value/(self.max_value+1))*100}%")
        self.percentage_label = ttk.Label(self.bottom_frame, textvariable=self.percentage_text)
        self.percentage_label.grid(column=0, row=2, columnspan=2)
        self.percentage_title = tk.StringVar()
        self.percentage_title.set("Percentage")
        self.percentage_title_label = tk.Label(self.bottom_frame, textvariable=self.percentage_title)
        self.percentage_title_label.grid(column=0, row=0, columnspan=2)

        # ListBox
        self.url_listbox = tk.Listbox(self.middle_frame, height=12)
        self.url_listbox.grid(column=0, row=1, columnspan=3, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.url_listbox, 0, weight=1)

        # Entries
        self.url_entry = tk.Text(self.top_frame, height=9)
        tk.Grid.columnconfigure(self.url_entry, 0, weight=1)
        self.url_entry.bind("<Tab>", self.focus_next_widget)
        self.refresh_list()
        self.url_entry.grid(column=0, row=2, columnspan=3, sticky='NSEW')

        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.bottom_frame, orient="horizontal",
            length=300, mode="determinate"
        )
        self.progress_bar.grid(column=0, row=1, padx=15, pady=10, columnspan=3, sticky='NSEW')

    def run(self, func, name=None):
        threading.Thread(target=func, name=name).start()

    # This class handles [TAB] Key to move to next Widget
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def open_file(self):
        name = askopenfilename(initialdir=os.getcwd(),
                               filetypes=(("Text File", "*.txt"), ("All Files", "*.*")),
                               title="Choose a file."
                               )
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            youtube_urls = open(name, 'r')
            print("youtube_urls", youtube_urls)
            print("Length of Links Before Open File: ", len(self.url_list))
            for url in youtube_urls:
                self.url_list.append(url)
            self.refresh_list()
            self.status.set(f'Loaded {len(self.url_list)} URLs from file: {name}')
        except:
            print("No file exists")
            self.status.set(f'File Not Found')

    def refresh_list(self):
        self.url_listbox.delete(0, tk.END)
        self.url_list = list(dict.fromkeys(self.url_list))
        for items in self.url_list:
            self.url_listbox.insert(tk.END, items)

    def add_url(self):
        parse_addition = self.url_entry.get("1.0", tk.END)
        parse_addition_array = parse_addition.splitlines()
        for url in parse_addition_array:
            if re.sub(r'[^A-Za-z0-9_./:?!=]', '', url) != "":
                self.status.set(f'Added URLs to Queue')
                temp = re.sub(r'[^A-Za-z0-9_./:?!=]', '', url)
                self.url_list.append(temp)
            else:
                print("Bad URL: ", url)
                self.status.set(f'Empty URL: {url}')
        self.url_list = list(dict.fromkeys(self.url_list))
        self.url_entry.delete("1.0", tk.END)
        self.refresh_list()

    def remove_url(self):
        if self.url_listbox.curselection():
            url = self.url_listbox.get(self.url_listbox.curselection())
            url = url.rstrip()
            self.status.set(f'Removed URL: {url}')
            print("Removing URL: ", self.url_listbox.get(self.url_listbox.curselection()))
            self.url_list.remove(self.url_listbox.get(self.url_listbox.curselection()))
            self.refresh_list()
        else:
            print("Click on a link to remove")
            self.status.set(f'Click on a URL to remove')

    def download_video_threaded(self, tkt_wrap):
        self.status.set(f'Downloading {len(self.url_list)} URLs')
        self.download_button_video["state"] = "disabled"
        self.download_button_audio["state"] = "disabled"
        self.value = 0
        th = threading.current_thread()
        self.url_list = list(filter(None, self.url_list))
        self.url_list = list(dict.fromkeys(self.url_list))
        self.max_value = len(self.url_list)
        self.progress_bar['maximum'] = self.max_value
        self.progress_bar['value'] = 0
        self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value / self.max_value) * 100}%")
        i = 0
        for url in self.url_list:
            self.youtube_downloader.append_link(url)
            print("LInks Sent: ", self.youtube_downloader.get_link())
            self.youtube_downloader.download_hd_videos()
            self.youtube_downloader.reset_links()
            txt = 'Progress: %02i' % (i + 1)
            print(th, txt)  # send to terminal
            self.value = i + 1
            self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value / self.max_value) * 100}%")
            self.progress_bar['value'] = i + 1
            print("Value: ", self.value)
            print("Max Value: ", self.max_value)
            # tkt_wrap(entry.delete, '0', 'end')
            # tkt_wrap(entry.set(txt))
            self.status.set(f'Completed {self.value}/{self.max_value}')
            i += 1
        self.download_button_video["state"] = "enabled"
        self.download_button_audio["state"] = "enabled"
        self.status.set(f'Downloaded {self.value} videos!')

    def download_audio_threaded(self, tkt_wrap):
        self.status.set(f'Downloading {len(self.url_list)} URLs')
        self.download_button_video["state"] = "disabled"
        self.download_button_audio["state"] = "disabled"
        self.value = 0
        th = threading.current_thread()
        self.url_list = list(filter(None, self.url_list))
        self.url_list = list(dict.fromkeys(self.url_list))
        self.max_value = len(self.url_list)
        self.progress_bar['maximum'] = self.max_value
        self.progress_bar['value'] = 0
        self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value / self.max_value) * 100}%")
        i = 0
        for url in self.url_list:
            self.youtube_downloader.append_link(url)
            self.youtube_downloader.download_audio()
            self.youtube_downloader.reset_links()
            txt = 'Progress: %02i' % i
            print(th, txt)  # send to terminal
            self.value = i + 1
            self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value / self.max_value) * 100}%")
            self.progress_bar['value'] = i + 1
            print("Value: ", self.value)
            print("Max Value: ", self.max_value)
            # tkt_wrap(entry.delete, '0', 'end')
            # tkt_wrap(entry.set(txt))
            self.status.set(f'Completed {self.value}/{self.max_value}')
            i += 1
        self.download_button_video["state"] = "enabled"
        self.download_button_audio["state"] = "enabled"
        self.status.set(f'Downloaded {self.value} videos!')

    def download_videos(self):
        self.run(lambda: self.download_video_threaded(self.tkt.nosync), name='NoSync')

    def download_audios(self):
        self.run(lambda: self.download_audio_threaded(self.tkt.nosync), name='NoSync')


root = tk.Tk()
root.title("Genius Web Archiver")
root.geometry("500x700")
root.minsize(500, 700)
tkt = TkThread(root)  # make the thread-safe callable
main_ui = GeniusBot(root, tkt)
root.mainloop()
