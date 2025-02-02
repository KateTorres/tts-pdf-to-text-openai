import os
import tkinter as tk
from tkinter import filedialog

def select_pdf_file(last_directory=os.getcwd()):
    """
    Opens a file selection dialog for choosing a PDF file, defaulting to last accessed directory.
    
    Returns:
        str: The selected file path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")],
        initialdir=last_directory
    )

    return file_path
