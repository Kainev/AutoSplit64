import time
from threading import Thread

from as64.constants import (
    FadeStatus
)


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
    def __init__(self) -> None:
        self._running: bool = False
        self._game_status = GameStatus()
        self._game_controller = GameController()
        
    def run(self) -> None:
        self._running = True

        while self._running:
            self._game_status.current_time = time.time()
            
            
            # Attempt to run main loop at given FPS
            try:
                self._game_status.delta = time.time() - self._game_status.current_time
                time.sleep(1 / self._game_status.fps - self._game_status.delta)
            except ValueError:
                pass

    def stop(self) -> None:
        self._running = False
