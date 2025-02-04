# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os

import win32api
import win32con
import win32gui
import win32process

import as64.config as config

from as64.enums import Region, Version


class GameCapture(object):
    def __init__(self, version, game_region, capture_plugin):
        self._version = version
        self._game_region = game_region
 
        self._regions = _generate_regions(game_region, version)
        
        self._capture_plugin = capture_plugin

        self._game_image = None
        self._region_images = {}
        
    def capture(self):
        self._game_image = self._capture_plugin.capture() 
        self._region_images.clear()
        
    def region_image(self, region: Region):
        if region in self._region_images:
            return self._region_images[region]
        
        try:
            self._region_images[region] = self._get_crop(*self._regions[region])
            return self._region_images[region]
        except KeyError:
            return None
        
    def region_rect(self, region: Region):
        try:
            return self._regions[region]
        except KeyError:
            return None
        
    def _get_crop(self, x, y, width, height):
        # TODO: Add a crop function util class for plugins developers?
        return self._game_image[y:y + height, x:x + width]
    
def _calculate_region(game_region, region_ratio) -> list:
    return [
        int(round(game_region[0] + (game_region[2] * region_ratio[0]))),
        int(round(game_region[1] + (game_region[3] * region_ratio[1]))),
        int(round(game_region[2] * region_ratio[2])),
        int(round(game_region[3] * region_ratio[3]))
    ]


def _generate_regions(game_region, version):
    # Calculated regions
    regions = {}
    
    # Generate system regions
    system_ratios = config.get('regions', 'system')
    
    regions[Region.GAME] = game_region
    
    if version == Version.JP:
        regions[Region.STAR] = _calculate_region(game_region, system_ratios['star_JP'])
        regions[Region.LIFE] = _calculate_region(game_region, system_ratios['life_JP'])
    else:
        regions[Region.STAR] = _calculate_region(game_region, system_ratios['star_US'])
        regions[Region.LIFE] = _calculate_region(game_region, system_ratios['life_US'])
        
    regions[Region.FADEOUT] = _calculate_region(game_region, system_ratios['fadeout'])
    regions[Region.FADEIN] = _calculate_region(game_region, system_ratios['fadein'])
    regions[Region.RESET] = _calculate_region(game_region, system_ratios['reset'])
    regions[Region.NO_HUD] = _calculate_region(game_region, system_ratios['no_hud'])
    regions[Region.FINAL_STAR] = _calculate_region(game_region, system_ratios['final_star'])
    regions[Region.XCAM] = _calculate_region(game_region, system_ratios['xcam'])
        
    return regions
    
    
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
