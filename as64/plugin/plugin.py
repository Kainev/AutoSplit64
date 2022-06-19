from enum import Enum, auto


class Definition(object):
    class Schedule(Enum):
        FRAME = auto()
        ONCE = auto()
        TIMER =  auto()

    SCHEDULE = Schedule.FRAME

    SETTINGS = {}


class Plugin(object):
    # class Schedule(Enum):
    #     FRAME = auto()
    #     ONCE = auto()
    #     TIMER =  auto()

    # SCHEDULE = Schedule.FRAME

    # SETTINGS = {}

    def __init__(self):
        pass

    def intialize(self):
        pass

    def start(self):
        pass

    def execute(self):
        pass

    def stop(self):
        pass

    def exit(self):
        pass
