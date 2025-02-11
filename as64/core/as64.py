# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import time
from dataclasses import dataclass
from typing import Optional

from as64 import (
    config,
)

from as64.core.route import Route, Split, load as load_route
from as64.core.capture import GameCapture

from as64.enums import Version, FadeStatus, Camera, AS64Status
from as64.plugins import PluginManager, SplitPlugin, CapturePlugin

from as64 import api

@dataclass
class TimedEvent:
    started: float = 0.0
    stopped: float = 0.0


class GameState(object):
    def __init__(self, route, game_capture: GameCapture) -> None:
        # Timing
        self.current_time: float = 0        # Time the most recent analyzed frame occured
        self.last_split_time: float = 0     # Time the last split occured
        self.last_fade_out_time: float = 0  # Time the last fade-out began
        self.last_fade_in_time: float = 0   # Time the last fade-in began
        self.last_reset_time: float = 0     # Time the last reset occured
        self.delta: float = 0               # Amount of time the last frame took to execute
        
        self.x_cam = TimedEvent()
        self.mario_cam = TimedEvent()
        self.lakitu_cam = TimedEvent()
        self.save_menu = TimedEvent()
                
        # Game Status
        self.star_count: int = None
        self.fade_out_count: int = 0
        self.fade_in_count: int = 0
        self.x_cam_count: int = 0
        self.camera: Optional[Camera] = None
        self.in_bowser_fight: bool = False
        self.fade_status = FadeStatus.NO_FADE
        self.in_intro: bool = True

        # Prediction
        self.prediction: int = -1
        self.probability: float = 0

        # Route
        self.route: Route = route
        self.current_split: Split = route.splits[0]
        self.current_split_index: int = -1
        self.external_split_update: bool = False

        # Regions
        self.frame = game_capture.region_image
        self.region = game_capture.region_rect
        
        
class GameController(object):
    def __init__(self) -> None:
        self.fps: float = 29.97
        self.predict_star_count: bool = True
        self.count_fades: bool = False
        self.count_x_cams: bool = False
        self.allow_star_jump: bool = False
       
        self.undo = None
        self.skip = None
        self.split = None
        self.reset = None
        
    def _register_split_plugin(self, split_plugin):
        self.undo = split_plugin.undo
        self.skip = split_plugin.skip
        self.split = split_plugin.split
        self.reset = split_plugin.reset

class AS64(object):
    def __init__(self, plugin_manager: PluginManager, enqueue_message) -> None:
        self._plugin_manager = plugin_manager
        self._enqueue_message = enqueue_message
        
        self._route = load_route(config.get('route', 'path'))
                
        self._capture_plugin: CapturePlugin = plugin_manager.get_active_plugin_classes(api.CapturePlugin)()           
            
        self._game_capture: GameCapture = GameCapture(Version.JP, config.get('capture', 'region'),  self._capture_plugin)
        self._game_state = GameState(self._route, self._game_capture)
        self._game_controller = GameController()
        
        # Register with API
        api.get_game_controller = self._get_game_controller
        api.get_game_state = self._get_game_state
        
        self._split_plugin: SplitPlugin = plugin_manager.get_active_plugin_classes(api.SplitPlugin)(self._game_state)
        
        self._game_controller._register_split_plugin(self._split_plugin)
        self._plugin_manager.instantiate_plugins(api.GameStatePlugin)
        self._plugin_manager.run_method(api.GameStatePlugin, "initialize", self._game_state, self._game_controller)
        
        self._game_state_plugins = plugin_manager.get_plugin_instances(api.GameStatePlugin)
        self._realtime_plugins = [plugin for plugin in plugin_manager.get_plugin_instances(api.Plugin) if plugin.is_realtime]
        
    def is_valid(self):
        if not self._capture_plugin.is_valid():
            return False
        if not self._split_plugin.is_valid():
            return False
        
        return True
        
    def _get_game_controller(self) -> GameController:
        return self._game_controller
    
    def _get_game_state(self) -> GameState:
        return self._game_state
    
    def _on_start(self) -> None:
        self._plugin_manager.run_method(api.GameStatePlugin, "start", self._game_state, self._game_controller)
        self._plugin_manager.run_method(api.Plugin, "start", self._game_state, self._game_controller)
        
    def _on_stop(self) -> None:
        self._plugin_manager.run_method(api.Plugin, "stop")
        
        self._plugin_manager.run_method(api.GameStatePlugin, "stop")
        self._plugin_manager.run_method(api.GameStatePlugin, "shutdown")
        
    def run(self, stop_event) -> None:
        self._on_start()
        self._enqueue_message({"event": "status", "data": AS64Status.RUNNING.value})
        
        while not stop_event.is_set():
            self._game_state.current_time = time.perf_counter()
            
            # Capture the current frame
            self._game_capture.capture()
            
            # Sync Split Plugin
            self._split_plugin.sync()
            
            # Execute GameState plugins
            for plugin in self._game_state_plugins:
                plugin.execute(self._game_state, self._game_controller)

            # # Execute Real Time Plugins
            for plugin in self._realtime_plugins:
                plugin.execute(self._game_state, self._game_controller)

            # Limit FPS
            try:
                self._game_state.delta = time.perf_counter() - self._game_state.current_time
                time.sleep(1 / self._game_controller.fps - self._game_state.delta)
            except ValueError:
                pass

        self._on_stop()
