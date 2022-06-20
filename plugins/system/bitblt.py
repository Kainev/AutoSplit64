# Plugin
from as64.plugin import CapturePlugin, Definition

# Python
import os
from ctypes import windll

# Win32
import win32gui
import win32ui
import win32con

# Numpy
import numpy as np


class BitBltDefinition(Definition):
    NAME = "BitBlt Capture"
    VERSION = "1.0.0"


class BitBlt(CapturePlugin):
    DEFINITION = BitBltDefinition
        
    def capture(self, hwnd):
        return _bit_blt(hwnd)
      
        
def _bit_blt(hwnd) -> np.array:
    """_summary_

    Args:
        hwnd (_type_): _description_

    Returns:
        np.array: _description_
    """
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    window_dc = win32gui.GetWindowDC(hwnd)
    img_dc = win32ui.CreateDCFromHandle(window_dc)
    mem_dc = img_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(bitmap)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)

    img = bitmap.GetBitmapBits(True)
    info = bitmap.GetInfo()
    img = np.fromstring(img, np.uint8).reshape(info['bmHeight'], info['bmWidth'], 4)[:, :, :3]

    img_dc.DeleteDC()
    mem_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, window_dc)
    win32gui.DeleteObject(bitmap.GetHandle())

    return img

def print_window(hwnd):
    """
    Capture the window of a given handle using the windows PrintWindow method.
    :param hwnd: Window Handle
    :return: Numpy Array
    """
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top

    window_dc = win32gui.GetWindowDC(hwnd)
    img_dc = win32ui.CreateDCFromHandle(window_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(img_dc, w, h)

    mem_dc.SelectObject(bitmap)

    windll.user32.PrintWindow(hwnd, mem_dc.GetSafeHdc(), 0)

    bmp_info = bitmap.GetInfo()
    bmp_str = bitmap.GetBitmapBits(True)

    image = np.fromstring(bmp_str, np.uint8).reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)[:, :, :3]

    win32gui.DeleteObject(bitmap.GetHandle())
    mem_dc.DeleteDC()
    img_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, window_dc)

    return image