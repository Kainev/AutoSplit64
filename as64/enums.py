# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

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
    CAMERA = auto()
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
    
    ENTER_LAKITU_CAMERA = auto()
    EXIT_LAKITU_CAMERA = auto()
    ENTER_MARIO_CAMERA = auto()
    EXIT_MARIO_CAMERA = auto()
    ENTER_X_CAMERA = auto()
    EXIT_X_CAMERA = auto()
    
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
    

class Camera(Enum):
    LAKITU = auto()
    MARIO = auto()
    XCAM = auto()
    NONE = auto()
        
        
class SplitType(Enum):
    STAR = "Star"
    BOWSER = "Bowser"
    LBLJ = "LBLJ"
    MIPS = "Mips"
    CUSTOM = "Custom"
