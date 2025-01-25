# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import time

from as64 import (
    config,
)

from as64.enums import Version
from as64.plugins import PluginManager, SplitPlugin
from as64.core.capture import GameCapture


class GameStatus(object):
    def __init__(self, route, game_capture: GameCapture) -> None:
        # Timing
        self.current_time: float = 0        # Time the most recent analyzed frame occured
        self.last_split_time: float = 0     # Time the last split occured
        self.last_fade_out_time: float = 0  # Time the last fade-out began
        self.last_fade_in_time: float = 0   # Time the last fade-in began
        self.last_reset_time: float = 0     # Time the last reset occured
        self.last_x_cam_time: float = 0     # Time the last x-cam began
        self.delta: float = 0               # Amount of time the last frame took to execute
        
        # Game Status
        self.star_count: int = None
        self.fade_out_count: int = 0
        self.fade_in_count: int = 0
        self.x_cam_count: int = 0
        self.in_x_cam: bool = False
        self.in_bowser_fight: bool = False
        # self.fade_status = FadeStatus.NO_FADE
        self.in_intro: bool = True

        # Prediction
        self.prediction: int = -1
        self.probability: float = 0

        # Route
        # self.route: Route = route
        # self.current_split: Split = route.splits[0]
        self.current_split_index: int = -1
        self.external_split_update: bool = False

        # Regions
        # self.get_region = game_capture.region_image
        # self.region_rect = game_capture.region_rect

class GameController(object):
    def __init__(self, split_plugin) -> None:
        self.fps: float = 29.97
        self.predict_star_count: bool = True
        self.count_fades: bool = False
        self.count_x_cams: bool = False
        self.allow_star_jump: bool = False
       
        # self.undo = split_plugin.undo
        # self.skip = split_plugin.skip
        # self.split = split_plugin.split
        # self.reset = split_plugin.reset

class AS64(object):
    def __init__(self, plugin_manager: PluginManager, event_emitter) -> None:
        self._plugin_manager = plugin_manager
        
        self._game_capture: GameCapture = GameCapture(Version.JP, config.get('capture', 'region'),  plugin_manager.get_capture_instance())
        self._game_status = GameStatus(None, None)
        self._split_plugin: SplitPlugin = plugin_manager.get_split_instance(self._game_status)
        self._game_controller = GameController(None)
        
        self._plugin_manager.start_lifecycle_plugins()
        
        
    def run(self) -> None:
        self._game_status.current_time = time.perf_counter()
        
        # Capture the current frame
        self._game_capture.capture()
        
        # Sync Split Plugin
        self._split_plugin.sync()
        
        # Execute GameState plugins
        for plugin in self._plugin_manager.game_state_plugins:
            plugin.execute(None)
            
        # Execute Real Time Plugins
        for plugin in self._plugin_manager.realtime_plugins:
            plugin.execute(None)
                        
        # Limit FPS
        try:
            self._game_status.delta = time.perf_counter() - self._game_status.current_time
            time.sleep(1 / self._game_controller.fps - self._game_status.delta)
        except ValueError:
            pass
        
        
        
