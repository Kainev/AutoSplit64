from . import constants

from . import config


#
# Constants
#

DEFAULT_FRAME_RATE = constants.DEFAULT_FRAME_RATE
DEFAULT_LS_HOST = constants.DEFAULT_LS_HOST
DEFAULT_LS_PORT = constants.DEFAULT_LS_PORT
GAME_JP = constants.GAME_JP
GAME_US = constants.GAME_US
TIMING_RTA = constants.TIMING_RTA
TIMING_UP_RTA = constants.TIMING_UP_RTA
TIMING_FILE_SELECT = constants.TIMING_FILE_SELECT
PREDICTION_MODE = constants.PREDICTION_MODE
CONFIRMATION_MODE = constants.CONFIRMATION_MODE
SPLIT_INITIAL = constants.SPLIT_INITIAL
SPLIT_NORMAL = constants.SPLIT_NORMAL
SPLIT_FADE_ONLY = constants.SPLIT_FADE_ONLY
SPLIT_FINAL = constants.SPLIT_FINAL
SPLIT_MIPS = constants.SPLIT_MIPS
SPLIT_MIPS_X = constants.SPLIT_MIPS_X
SPLIT_XCAM = constants.SPLIT_XCAM
NO_FADE = constants.NO_FADE
FADEOUT_PARTIAL = constants.FADEOUT_PARTIAL
FADEOUT_COMPLETE = constants.FADEOUT_COMPLETE
FADEIN_PARTIAL = constants.FADEIN_PARTIAL
FADEIN_COMPLETE = constants.FADEIN_COMPLETE
GAME_REGION = constants.GAME_REGION
STAR_REGION = constants.STAR_REGION
LIFE_REGION = constants.LIFE_REGION
NO_HUD_REGION = constants.NO_HUD_REGION
RESET_REGION = constants.RESET_REGION
FADEOUT_REGION = constants.FADEOUT_REGION
FADEIN_REGION = constants.FADEIN_REGION
POWER_REGION = constants.POWER_REGION
XCAM_REGION = constants.XCAM_REGION


#
# Route Class
#

class Route(object):
    def insert_split(self, index) -> None:
        pass

    def remove_split(self, index) -> None:
        pass


#
# Split Class
#

class Split(object):
    pass


#
# Base
#
ls_host: str = DEFAULT_LS_HOST
ls_port: int = DEFAULT_LS_PORT

fps: float = DEFAULT_FRAME_RATE
current_time: float = 0.0
game_version: str = GAME_JP
route = Route()
route_length: int = 0
star_count: int = 0
previous_split_initial_star: int = 0
next_split_split_star: int = 0
last_split: int = 0
collection_time: int = 0
xcam_count: int = 0
xcam_percent: float = 0.0
in_xcam: bool = False
fadeout_count: int = 0
fadein_count: int = 0
fade_status: str = NO_FADE
prediction_info = None
execution_time: float = 0.0
start_on_reset: bool = True


def init() -> None:
    import sys
    from .base import Base

    module = sys.modules[__name__]

    Base(module)


def start() -> None:
    pass


def stop() -> None:
    pass


def set_star_count(p_int: int) -> None:
    pass


def enable_predictions(enable: bool) -> None:
    pass


def enable_fade_count(enable: bool) -> None:
    pass


def enable_xcam_count(enable: bool) -> None:
    pass


def set_in_game(ended: bool) -> None:
    pass

def get_region(region):
    pass


def get_region_rect(region) -> list:
    pass


def register_split_processor(split_type, processor) -> None:
    pass


#
# Split Functions
#

def split() -> None:
    pass


def reset() -> None:
    pass


def skip() -> None:
    pass


def undo() -> None:
    pass


#
# Tracking Functions
#

def fadeout() -> None:
    pass


def fadein() -> None:
    pass


def increment_star() -> None:
    pass


def incoming_split(star_count: bool = True, fadeout: bool = True, fadein: bool = True) -> bool:
    pass


def current_split():
    pass


def split_index() -> int:
    pass


#
# Route
#

def load() -> Route:
    pass


def save() -> None:
    pass


#
# Listeners
#

def set_update_listener(listener) -> None:
    pass


def set_error_listener(listener) -> None:
    pass


def force_update() -> None:
    pass