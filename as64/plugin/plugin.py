from enum import Enum, auto


class Definition(object):
    class Schedule(Enum):
        FRAME = auto()
        ONCE = auto()
        TIMER =  auto()

    SCHEDULE = Schedule.FRAME

    SETTINGS = {}
    

class BasePlugin(object):
    DEFINITION = None
    
    def __init__(self):
        pass
    
    def initialize(self):
        pass
    
    def is_valid(self):
        return True
        

class CapturePlugin(BasePlugin):
    def capture(self, hwnd):    
        pass
    
    
class SplitPlugin(BasePlugin):
    def split(self):
        pass
    
    def skip(self):
        pass
    
    def undo(self):
        pass
    
    def reset(self):
        pass
    

class Plugin(BasePlugin):
    def __init__(self):
        pass

    def start(self):
        pass

    def execute(self):
        pass

    def stop(self):
        pass

    def exit(self):
        pass