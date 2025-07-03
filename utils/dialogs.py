# Message box to select file

import tkinter as tk
from tkinter import messagebox

def show_info(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
