import threading
import tkinter as tk

import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure


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

'''
app = App()
print('Now we can continue running code while mainloop runs!')

for i in range(3):
    print(i)
    time.sleep(1)
'''
