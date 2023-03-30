import time

from pymitter import EventEmitter

from as64.constants import (
    FadeStatus,
    Version
)

from as64 import config
from as64.capture import GameCapture, get_handle


from as64.plugin.plugin import Plugin, SplitPlugin
from as64 import route
from as64.route import Route, Split


class GameStatus(object):
    def __init__(self, route: Route, game_capture: GameCapture) -> None:
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
        self.get_region = game_capture.region_image
        self.region_rect = game_capture.region_rect
        # self.export_region_image = None


class GameController(object):
    def __init__(self, split_plugin) -> None:
        self.fps: float = 6
        self.predict_star_count: bool = True
        self.count_fades: bool = False
        self.count_x_cams: bool = False
       
        self.undo = split_plugin.undo
        self.skip = split_plugin.skip
        self.split = split_plugin.split
        self.reset = split_plugin.reset
        

class GameEvent(object):
    def __init__(self, status: GameStatus,  controller: GameController, emitter: EventEmitter):
        self.status: GameStatus = status
        self.controller: GameController = controller
        self.emitter: EventEmitter = emitter


class AS64(object):
    def __init__(self, system_plugins: dict, user_plugins: list=[]) -> None:
        self._running: bool = False
        
        self._hwnd = get_handle(config.get('capture', 'process'))
        self._game_capture: GameCapture = GameCapture(self._hwnd, Version.JP, config.get('capture', 'region'), system_plugins[config.get('plugins', 'system', 'capture')])
        
        # Instantiate system plugins
        self._split_plugin: SplitPlugin = system_plugins[config.get('plugins', 'system', 'split')]()
        self._fade_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'fade')]()
        self._star_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'star')]()
        self._xcam_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'xcam')]()
        self._logic_plugin: Plugin = system_plugins[config.get('plugins', 'system', 'logic')]()
                
        # Store user plugins (User plugins are initialized on AS64 launch)
        self._user_plugins: list = user_plugins
        
        # Event System
        self._event_emitter = EventEmitter()
        
        # Game Status/Controller
        self._game_status = GameStatus(route.load(config.get('route', 'path')), self._game_capture)
        self._game_controller = GameController(self._split_plugin)
        self._game_event = GameEvent(self._game_status, self._game_controller, self._event_emitter)
        
        # Initialize Plugins
        self._initialize_system_plugins()
        
    def run(self) -> None:
        self._running = True
        self._start_plugins(self._game_event)
        
        while self._running:
            self._game_status.current_time = time.time()
            
            # Capture the game window
            self._game_capture.capture()
            
            # Execute system plugins
            self._split_plugin.execute(self._game_event)
            self._fade_plugin.execute(self._game_event)
            self._xcam_plugin.execute(self._game_event)
            self._star_plugin.execute(self._game_event)
            self._logic_plugin.execute(self._game_event)
            
            # Execute user plugins
            for plugin in self._user_plugins:
                plugin.execute(self._game_event)

            # Limit FPS 
            try:
                self._game_status.delta = time.time() - self._game_status.current_time
                time.sleep(1 / self._game_controller.fps - self._game_status.delta)
            except ValueError:
                pass

    def stop(self) -> None:
        self._running = False
        
        self._split_plugin.stop(self._game_event)
        self._fade_plugin.stop(self._game_event)
        self._star_plugin.stop(self._game_event)
        self._xcam_plugin.stop(self._game_event)
        self._logic_plugin.stop(self._game_event)
        
        for plugin in self._user_plugins:
            plugin.stop(self._game_event)

    def _initialize_system_plugins(self):
        self._split_plugin.initialize(self._game_event)
        self._fade_plugin.initialize(self._game_event)
        self._star_plugin.initialize(self._game_event)
        self._xcam_plugin.initialize(self._game_event)
        self._logic_plugin.initialize(self._game_event)
        
    def _start_plugins(self, ev):
        self._split_plugin.start(self._game_event)
        self._fade_plugin.start(ev)
        self._star_plugin.start(ev)
        self._xcam_plugin.start(ev)
        self._logic_plugin.start(ev)
        
        for plugin in self._user_plugins:
            plugin.start(ev)
            
    def _validity_check(self):
        return True
