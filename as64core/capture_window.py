from ctypes import windll
import win32gui
import win32ui
import win32process
import numpy as np
import psutil

EXCLUSION_LIST = ["ApplicationFrameHost.exe",
                  "WinRAR.exe",
                  "notepad.exe",
                  "WWAHost.exe",
                  "SystemSettings.exe",
                  "WinStore.App.exe",
                  "Taskmgr.exe",
                  "Video.UI.exe",
                  "notepad++.exe",
                  "pycharm64.exe",
                  "cmd.exe",
                  "python.exe",
                  "explorer.exe",
                  "Calculator.exe",
                  "Discord.exe"]


def get_visible_processes():
    """ Returns a list of processes with a valid hwnd """
    processes = []
    for proc in psutil.process_iter():
        hwnd = 0
        try:
            # Get process name & pid from process object.
            process_name = proc.name()
            process_id = proc.pid

            if process_id is not None:
                def callback(h, additional):
                    if win32gui.IsWindowVisible(h) and win32gui.IsWindowEnabled(h):
                        _, p = win32process.GetWindowThreadProcessId(h)
                        if p == process_id:
                            additional.append(h)
                        return True
                    return True

                additional = []
                win32gui.EnumWindows(callback, additional)

                if additional:
                    hwnd = additional[0]

            if hwnd and process_name not in EXCLUSION_LIST:
                processes.append((proc, hwnd))

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return processes


def get_hwnd_from_list(process_name, process_list):
    """ Given a list of processes, return process with given name """
    for p in process_list:
        if p[0].name() == process_name:
            return p[1]


def capture(hwnd):
    """
    https://stackoverflow.com/a/24352388
    """
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top


    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)

    save_dc.SelectObject(save_bitmap)

    result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

    bmp_info = save_bitmap.GetInfo()
    bmp_str = save_bitmap.GetBitmapBits(True)

    image = np.fromstring(bmp_str, np.uint8).reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)[:,:,:3]

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    return image


def get_capture_size(hwnd):
    left, top, right, bot = win32gui.GetWindowRect(hwnd)

    return [right - left, bot - top]

