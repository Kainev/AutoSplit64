from enum import Enum, Flag, auto


class Version(Enum):
    AUTO = "Auto"
    JP = "JP"
    US = "US"


class SplitType(Enum):
    STAR = "Star"
    BOWSER = "Bowser"
    LBLJ = "LBLJ"
    MIPS = "Mips"
    CUSTOM = "Custom"
    
    
class Event(object):
    EXTERNAL_SPLIT_UPDATE = 'EXTERNAL_SPLIT_UPDATE'
    STAR_COLLECTED = 'STAR_COLLECTED'

class FadeStatus(Flag):
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
    FINAL_STAR = auto()


USER_PLUGIN_DIR = 'plugins'
SYSTEM_PLUGIN_DIR = 'plugins/system'
