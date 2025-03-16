import win32print
import win32gui
import os

def getCurrentMonitorFramerate():
    """
    gets the current monitor's refresh rate
    """
    dc = win32gui.GetDC(0)  # get device context
    framerate = win32print.GetDeviceCaps(dc, 116)  # get refresh rate of the monitor
    win32gui.ReleaseDC(0, dc)  # release device context
    return framerate

def count_sounds_in_directory(directory):
    if not os.path.exists(directory): # if the directory does not exist
        return 0
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.wav')]) # return the number of files in the directory that end with .wav