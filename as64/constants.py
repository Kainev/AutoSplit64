from enum import Enum, Flag, auto


class Version(Enum):
    AUTO = "Automatic"
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
    SPLIT = 'SPLIT'
    SKIP = 'SKIP'
    UNDO = 'UNDO'
    RESET = 'RESET'
    STAR_COLLECTED = 'STAR_COLLECTED'
    ENTER_XCAM = 'ENTER_XCAM'
    EXIT_XCAM = 'EXIT_XCAM'
    FADEOUT_BEGIN = 'FADEOUT_BEGIN'
    FADEOUT_COMPLETE = 'FADEOUT_COMPLETE'
    FADEOUT_END = 'FADEOUT_END'
    FADEIN_BEGIN = 'FADEIN_BEGIN'
    FADEIN_COMPLETE = 'FADEIN_COMPLETE'
    FADEIN_END = 'FADEIN_END'
    DEATH = 'DEATH'
    ENTER_SAVE_MENU = 'ENTER_SAVE_MENU'
    EXIT_SAVE_MENU = 'EXIT_SAVE_MENU'
    BOWSER_FIGHT = 'BOWSER_FIGHT'
    GAME_START = 'GAME_START'
    

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
