# Plugin
from as64.plugin import Plugin 

# Python
import os
from ctypes import windll

# Win32
import win32gui
import win32ui
import win32con
import win32api
import win32process



class Capture(Plugin):
    NAME = "Program Capture"
    VERSION = "1.0"

    def __init__(self):
        self.image = None

    def initialize(self):
        pass
        
    def execute(self, ev):
        hwnd = None
        
