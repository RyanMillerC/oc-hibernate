import os
import sys


def get_resource_path(relative_path):
    """Get absolute path to resource. Works for dev and for PyInstaller.
    https://stackoverflow.com/a/31966932
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
