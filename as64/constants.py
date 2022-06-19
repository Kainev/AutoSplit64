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
