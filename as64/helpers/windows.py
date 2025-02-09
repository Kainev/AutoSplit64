# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import win32gui
import win32process
import win32api
import win32con
import psutil

from as64.ipc import rpc

def enum_window_callback(hwnd, pid_set):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pid_set.add(pid)

@rpc.register("windows.visible_process_names")
def visible_process_names():
    pid_set = set()
    # Enumerate top-level windows
    win32gui.EnumWindows(enum_window_callback, pid_set)
    
    processes = []
    for pid in pid_set:
        try:
            proc = psutil.Process(pid)
            processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        
    return [process.name() for process in processes]


def _get_window_handles():
    handles = []
    
    def foreach_hwnd(hwnd, other):
        if win32gui.IsWindowVisible(hwnd):
            handles.append(hwnd)
            
    win32gui.EnumWindows(foreach_hwnd, None)
    
    return handles


def get_handle(name: str):
    handles = _get_window_handles()
    
    for handle in handles:
        pid = win32process.GetWindowThreadProcessId(handle)
        hdl = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid[1])
        process_name = os.path.basename(win32process.GetModuleFileNameEx(hdl, 0))
        
        if process_name == name:
            return handle
        
    return None