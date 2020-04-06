import time
import threading
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
        self.root = root_main
        self.tkt = tkt_main
        self.youtube_downloader = YouTubeDownloader()
        # Frame UI
        tk.Grid.rowconfigure(self.root, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.root, 0, minsize=1, weight=1)
        self.main_frame = tk.Frame(self.root)
        #tk.Grid.rowconfigure(self.main_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.main_frame, 0, minsize=1, weight=1)
        self.top_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.top_frame, 0, minsize=1, weight=1)
        #tk.Grid.columnconfigure(self.top_frame, 0, minsize=1, weight=1)
        self.middle_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.middle_frame, 1, minsize=1, weight=2)
        tk.Grid.columnconfigure(self.middle_frame, 0, minsize=1, weight=1)
        self.bottom_frame = tk.Frame(self.main_frame)
        tk.Grid.rowconfigure(self.bottom_frame, 0, minsize=1, weight=1)
        tk.Grid.columnconfigure(self.bottom_frame, 0, minsize=1, weight=1)
        self.notification_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky='NSEW')
        self.top_frame.grid(row=0, column=0, sticky='NSEW')
        self.middle_frame.grid(row=1, column=0, sticky='NSEW')
        self.bottom_frame.grid(row=2, column=0, sticky='NSEW')
        self.notification_frame.grid(row=3, column=0, sticky='NSEW')

        # Buttons
        self.add_url_button = ttk.Button(self.middle_frame, text="Add", command=self.add_url)
        tk.Grid.rowconfigure(self.add_url_button, 0, minsize=1, weight=0)
        self.add_url_button.grid(column=0, row=1, sticky='NSEW', padx=15, pady=10)
        self.remove_url_button = ttk.Button(self.middle_frame, text="Remove", command=self.remove_url)
        self.remove_url_button.grid(column=1, row=1, sticky='NSEW', padx=15, pady=10)
        self.openfile_button = ttk.Button(self.middle_frame, text="Open File", command=self.open_file)
        self.openfile_button.grid(column=2, row=1, sticky='NSEW', padx=15, pady=10)
        self.download_button = ttk.Button(self.bottom_frame, text="Download", command=self.download_videos)
        self.download_button.grid(column=0, row=3, sticky='NSEW', padx=15, pady=10)

        # Labels
        self.title = tk.StringVar()
        self.title.set("GeniusBot - Web Archive")
        self.title_label = tk.Label(self.top_frame, textvariable=self.title)
        self.title_label.grid(column=0, row=0, sticky='NSEW')
        self.queue_title = tk.StringVar()
        self.queue_title.set("Video Download Queue")
        self.queue_title_label = tk.Label(self.middle_frame, textvariable=self.queue_title)
        self.queue_title_label.grid(column=0, row=2)
        self.w_text = tk.StringVar()
        self.w_text.set("Enter YouTube Link Below: ")
        self.w = tk.Label(self.top_frame, textvariable=self.w_text)
        self.w.grid(column=0, row=1, sticky='NSEW')
        self.percentage_text = tk.StringVar()
        self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value/(self.max_value+1))*100}%")
        self.percentage_label = ttk.Label(self.bottom_frame, textvariable=self.percentage_text)
        self.percentage_label.grid(column=0, row=2)
        self.percentage_title = tk.StringVar()
        self.percentage_title.set("Percentage")
        self.percentage_title_label = tk.Label(self.bottom_frame, textvariable=self.percentage_title)
        self.percentage_title_label.grid(column=0, row=0)

        # ListBox
        self.url_listbox = tk.Listbox(self.middle_frame, height=21)
        self.url_listbox.grid(column=0, row=3, columnspan=3, rowspan=3, sticky='NSEW')
        tk.Grid.columnconfigure(self.url_listbox, 0, weight=1)

        # Entries
        self.url_entry = tk.Text(self.middle_frame, height=9)
        tk.Grid.columnconfigure(self.url_entry, 0, weight=1)
        self.refresh_list()
        self.url_entry.grid(column=0, row=0, columnspan=3, sticky='NSEW')
        #self.url_entry.pack(fill=tk.BOTH, expand=tk.YES)
        #self.url_listbox.pack(fill=tk.BOTH, expand=tk.YES)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.bottom_frame, orient="horizontal",
            length=300, mode="determinate"
        )
        self.progress_bar.grid(column=0, row=1, padx=15, pady=10, columnspan=3, sticky='NSEW')

    def run(self, func, name=None):
        threading.Thread(target=func, name=name).start()

    def open_file(self):
        name = askopenfilename(initialdir="C:/Users/Batman/Documents/Programming/tkinter/",
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

            print("Length of Links After Open File: ", len(self.url_list))
            print(name)
        except:
            print("No file exists")

    def refresh_list(self):
        self.url_listbox.delete(0, tk.END)
        for items in self.url_list:
            self.url_listbox.insert(tk.END, items)
        self.url_list = list(dict.fromkeys(self.url_list))

    def add_url(self):
        parse_addition = self.url_entry.get("1.0", tk.END)
        parse_addition_array = parse_addition.splitlines()
        for url in parse_addition_array:
            temp = re.sub(r'[^A-Za-z0-9_./:?!]', '', url)
            self.url_list.append(temp)
        self.refresh_list()

    def remove_url(self):
        print("Removing URL: ", self.url_listbox.get(self.url_listbox.curselection()))
        self.url_list.remove(self.url_listbox.get(self.url_listbox.curselection()))
        self.refresh_list()

    def long_computation(self, entry, tkt_wrap):
        th = threading.current_thread()
        self.youtube_downloader.extend_link(self.url_list)
        self.youtube_downloader.download_hd_videos()
        self.max_value = len(self.url_list)
        self.progress_bar['maximum'] = self.max_value
        for i in range(self.max_value):
            txt = 'Progress: %02i' % i
            print(th, txt)  # send to terminal
            self.value = i + 1
            self.percentage_text.set(f"{self.value}/{self.max_value} | {(self.value / (self.max_value)) * 100}%")
            self.progress_bar['value'] = i+1
            print("Value: ", self.value)
            print("Max Value: ", self.max_value)
            #tkt_wrap(entry.delete, '0', 'end')
            #tkt_wrap(entry.set(txt))

            time.sleep(3)
            time.sleep(0.125)

    def download_videos(self):
        #YouTubeConnector(self.queue, self.value, self.max_value, self.progress_bar).start()
        #self.root.after(100, self.process_queue)
        self.run(lambda: self.long_computation(self.percentage_text, self.tkt.nosync), name='NoSync')

root = tk.Tk()
root.title("Genius Web Archiver")
root.geometry("500x700")
root.minsize(500, 700)
tkt = TkThread(root)  # make the thread-safe callable
main_ui = GeniusBot(root, tkt)
#main_ui.test()


root.mainloop()
