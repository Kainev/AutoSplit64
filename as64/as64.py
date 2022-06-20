import time
from threading import Thread

from as64.constants import (
    FadeStatus
)

from as64 import config
from as64.capture import GameCapture, get_handle

import cv2

from as64.plugin.plugin import Plugin

class GameStatus(object):
    def __init__(self) -> None:
        # Timing
        self.current_time = 0
        self.last_split_time = 0
        self.last_fade_out_time = 0
        self.last_fade_in_time = 0
        self.last_reset_time = 0
        self.x_cam_begin_time: int = 0
        self.delta: float = 0
        self.fps: float = 6

        # Game Status
        self.star_count: int = 0
        self.fade_out_count: int = 0
        self.fade_in_count: int = 0
        self.x_cam_count: int = 0
        self.in_x_cam: bool = False
        self.in_bowser_fight: bool = False
        self.fade_status = FadeStatus.NO_FADE

        # Prediction
        self.prediction: int = -1
        self.probability: float = 0

        # Route
        self.route = None
        self.current_split = None

        # Regions
        self.get_region = None
        self.get_region_rect = None
        self.export_region_image = None

        # Helper functions
        self.check_prediction = None


class GameController(object):
    def __init__(self) -> None:
        self.predict_star_count: bool = True
        self.count_fades: bool = False
        self.count_x_cams: bool = False
       
        self.undo = None
        self.split = None
        self.reset = None


class AS64(object):
    def __init__(self, system_plugins: dict, user_plugins: list=[]) -> None:
        self._running: bool = False
        self._game_status = GameStatus()
        self._game_controller = GameController()
        
        self._hwnd = get_handle(config.get('capture', 'process'))
        
        self._game_capture: GameCapture = GameCapture(self._hwnd, None, config.get('capture', 'region'), system_plugins[config.get('plugins', 'system', 'capture')])
        
        # Instantiate and initialize plugins
        self._split_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'split')]()
        self._fade_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'fade')]()
        self._star_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'star')]()
        self._xcam_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'xcam')]()
        self._logic_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'logic')]()
        
        self._split_plugin.initialize()
        self._fade_plugin.initialize()
        self._star_plugin.initialize()
        self._xcam_plugin.initialize()
        self._logic_plugin.initialize()
        
        self._user_plugins: list = user_plugins
        
    def run(self) -> None:
        self._running = True
        
        self._start_plugins()

        while self._running:
            self._game_status.current_time = time.time()
            
            # Capture the game window
            self._game_capture.capture()
            
            # Execute system plugins
            self._split_plugin.execute(None)
            self._fade_plugin.execute(None)
            self._xcam_plugin.execute(None)
            self._star_plugin.execute(None)
            self._logic_plugin.execute(None)
            
            # Execute user plugins
            for plugin in self._user_plugins:
                plugin.execute(None)
                        
            # Limit FPS 
            try:
                self._game_status.delta = time.time() - self._game_status.current_time
                time.sleep(1 / self._game_status.fps - self._game_status.delta)
            except ValueError:
                pass

    def stop(self) -> None:
        self._running = False
        
    def _start_plugins(self):
        self._fade_plugin.start()
        self._star_plugin.start()
        self._xcam_plugin.start()
        self._logic_plugin.start()
        
        for plugin in self._user_plugins:
            plugin.start()
