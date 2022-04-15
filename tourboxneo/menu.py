import logging
import toml
import time
import tkinter as tk
from tkinter import ttk
from threading import *

logger = logging.getLogger(__name__)

FONT = ('Verdana', 12)
NORM_FONT = ('Helvetica', 10)
SMALL_FONT = ('Helvetica', 8)


gui_thread = None

def start_tk(tk):
    tk.mainloop()


class Menu(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # basic setup
        self.overrideredirect(True)
        self.wm_title('TourBoxNeo Menu')

        # callbacks
        self.bind('<FocusIn>', self.focus_in)
        self.bind('<FocusOut>', self.focus_out)

        close = ttk.Button(self, text='x', command=self.destroy)
        close.pack(side='right')
        label = ttk.Label(self, text='foo', font=FONT)
        label.pack(side='top', fill='x', pady=10)

        # position
        abs_x = self.winfo_pointerx() - self.winfo_rootx()
        abs_y = self.winfo_pointery() - self.winfo_rooty()
        self.geometry('+{0}+{1}'.format(abs_x, abs_y))
        self.update_idletasks()

    def focus_in(self, event):
        print('focus in')

    def focus_out(self, event):
        print('focus out')
        self.destroy()
