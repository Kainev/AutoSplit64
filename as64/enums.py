from enum import Enum, Flag, auto

class StringEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Version(Enum):
    AUTO = "Automatic"
    JP = "JP"
    US = "US"


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
    
    
class Event(StringEnum):
    EXTERNAL_SPLIT_UPDATE = auto()
    SPLIT = auto()
    SKIP = auto()
    UNDO = auto()
    RESET = auto()
    STAR_COLLECTED = auto()
    ENTER_XCAM = auto()
    EXIT_XCAM = auto()
    FADEOUT_BEGIN = auto()
    FADEOUT_COMPLETE = auto()
    FADEOUT_END = auto()
    FADEIN_BEGIN = auto()
    FADEIN_COMPLETE = auto()
    FADEIN_END = auto()
    DEATH = auto()
    ENTER_SAVE_MENU = auto()
    EXIT_SAVE_MENU = auto()
    BOWSER_FIGHT = auto()
    GAME_START = auto()
    FINISHED = auto()
    
# class Event(Enum):
    # EXTERNAL_SPLIT_UPDATE = 'EXTERNAL_SPLIT_UPDATE'
    # SPLIT = 'SPLIT'
    # SKIP = 'SKIP'
    # UNDO = 'UNDO'
    # RESET = 'RESET'
    # STAR_COLLECTED = 'STAR_COLLECTED'
    # ENTER_XCAM = 'ENTER_XCAM'
    # EXIT_XCAM = 'EXIT_XCAM'
    # FADEOUT_BEGIN = 'FADEOUT_BEGIN'
    # FADEOUT_COMPLETE = 'FADEOUT_COMPLETE'
    # FADEOUT_END = 'FADEOUT_END'
    # FADEIN_BEGIN = 'FADEIN_BEGIN'
    # FADEIN_COMPLETE = 'FADEIN_COMPLETE'
    # FADEIN_END = 'FADEIN_END'
    # DEATH = 'DEATH'
    # ENTER_SAVE_MENU = 'ENTER_SAVE_MENU'
    # EXIT_SAVE_MENU = 'EXIT_SAVE_MENU'
    # BOWSER_FIGHT = 'BOWSER_FIGHT'
    # GAME_START = 'GAME_START'
    # FINISHED = 'FINISHED'
    
    
class SplitType(Enum):
    STAR = "Star"
    BOWSER = "Bowser"
    LBLJ = "LBLJ"
    MIPS = "Mips"
    CUSTOM = "Custom"
