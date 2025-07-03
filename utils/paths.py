# Open directory and remember where it was opened

import os

def get_directory(path):
    return os.path.dirname(path)

def get_basename(path):
    return os.path.basename(path)

def replace_suffix(path, suffix):
    base, _ = os.path.splitext(path)
    return base + suffix
