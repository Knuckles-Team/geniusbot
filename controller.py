from genius_bot import App
import tkinter as tk
import threading
import time
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


def main():
    app = App()
    print('Now we can continue running code while mainloop runs!')

    for i in range(3):
        print(i)
        time.sleep(1)


main()
