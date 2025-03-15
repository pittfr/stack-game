import win32print
import win32gui

def getCurrentMonitorFramerate():
    """
    gets the current monitor's refresh rate
    """
    dc = win32gui.GetDC(0)  # get device context
    framerate = win32print.GetDeviceCaps(dc, 116)  # get refresh rate of the monitor
    win32gui.ReleaseDC(0, dc)  # release device context
    return framerate