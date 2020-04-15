# Implement the default Matplotlib key bindings.
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk


class GeniusBot:
    progress_bar = None
    value = None
    max_value = None
    w_text = None

    def __init__(self, master):
        self.master = master
        self.test_button = ttk.Button(self.master, text="Test", command=self.tb_click)
        #self.test_button.configure(            text="Start", padx=50        )
        self.test_button.grid(column=0, row=1)
        self.queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.w_text = tk.StringVar()
        self.w_text.set("Text Before")
        self.value = tk.IntVar()
        self.value.set(0)
        self.max_value = tk.IntVar()
        self.max_value.set(0)
        self.w = tk.Label(self.master, textvariable=self.max_value)
        self.w.grid(column=2, row=2)

    def progress(self):
        print("Value of progress before: ", self.max_value.get())
        self.progress_bar = ttk.Progressbar(
            self.master, orient="horizontal",
            length=200, mode="determinate",
            variable=int(self.value.get()), maximum=int(self.max_value.get())
        )


    def tb_click(self):
        YouTubeConnector(self.queue, self.value, self.max_value, self.progress_bar).start()
        self.progress_bar.grid(column=1, row=1)
        print("Right Before: ", self.max_value.get())
        '''self.progress()
        self.progress_bar.start()'''
        self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.queue.get(0)
            print("MSG: ", msg)
            # Show result of the task if needed
            self.progress_bar.stop()
            self.progress_bar.grid_forget()
        except queue.Empty:
            self.master.after(100, self.process_queue)


class YouTubeConnector(threading.Thread):
    bar=None
    
    def __init__(self, queue_threads, video_num, video_max, bar):
        threading.Thread.__init__(self)
        self.video_max = video_max
        self.queue = queue_threads
        self.video_num = video_num
        self.bar = bar

    def run(self):
        x = [1, 2, 3]
        self.video_max.set(len(x))
        #self.bar["maximum"] = self.video_num.get()
        #self.bar["variable"] = self.video_max.get()
        print("Vid Max Calc: ", self.video_max.get())
        for i in x:
            #print("I: ", i)
            self.video_num.set(i)
            print(self.video_num.get())
            time.sleep(1)  # Simulate long running process
        self.queue.put("Task finished")


root = tk.Tk()
root.title("Test")
root.geometry("500x300")
main_ui = GeniusBot(root)
root.mainloop()

'''
class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def initialize(self):
        label = tk.Label(self.root, text="Hello World")
        label.grid(column=0,row=6,sticky='NSEW')
        test_label = tk.Label(self.root, text="Type Your Message:\n", bg="Black", fg="white", font="none 25 bold")
        test_label.grid(column=1,row=6,sticky='NSEW')
        Test_Text = tk.Text(self.root, width=15, height=3)
        Test_Text.bind("<Tab>", self.focus_next_widget)
        Test_Text.grid(column=2,row=6,sticky='NSEW')
        frame=tk.Frame(self.root)
        frame.grid(row=0, column=0, columnspan=3, sticky='NSEW')
        for row_index in range(5):
            tk.Grid.rowconfigure(frame, row_index, weight=1)
            for col_index in range(10):
                tk.Grid.columnconfigure(frame, col_index, weight=1)
                btn = tk.Button(frame) #create a button inside frame
                btn.grid(row=row_index, column=col_index, sticky='NSEW')

    # This class handles [TAB] Key to move to next Widget
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    # Handles Loading Matplotlib
    def matplotlib_canvas(self):
        frame2=tk.Frame(self.root)
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        canvas = FigureCanvasTkAgg(fig, master=self.root)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.root)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.columnconfigure(self.root, 0, weight=1)

        self.initialize()
        #self.matplotlib_canvas()
        self.root.title("Test")
        self.root.geometry("500x300")
        self.root.mainloop()

''''''
app = App()
print('Now we can continue running code while mainloop runs!')

for i in range(3):
    print(i)
    time.sleep(1)
'''
