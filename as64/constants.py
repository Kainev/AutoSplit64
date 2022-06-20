from enum import Enum, auto


class Version(Enum):
    AUTO = "Auto"
    JP = "JP"
    US = "US"


class FadeStatus(Enum):
    NO_FADE = auto()
    FADE_OUT_PARTIAL = auto()
    FADE_OUT_COMPLETE = auto()
    FADE_IN_PARTIAL = auto()
    FADE_IN_COMPLETE = auto()
    
    
class Region(Enum):
    GAME = auto()
    STAR = auto()
    LIFE = auto()
    FADEOUT = auto()
    FADEIN = auto()
    RESET = auto()
    NO_HUD = auto()
    XCAM = auto()


USER_PLUGIN_DIR = 'plugins'
SYSTEM_PLUGIN_DIR = 'plugins/system'
