from enum import Enum, auto


class Definition(object):
    class Execution(Enum):
        FRAME = auto()
        EVENT_ONLY = auto()

    class Type(Enum):
        USER = auto()
        SYSTEM = auto()

    NAME = None
    VERSION = None
    AUTHOR = None
    TYPE = Type.USER
    EXECUTION = Execution.FRAME


class BasePlugin(object):
    DEFINITION = None
    
    def __init__(self):
        pass

    def initialize(self, ev=None):
        pass
    
    def ready(self, ev=None):
        pass

    def start(self, ev=None):
        pass

    def stop(self, ev=None):
        pass

    def exit(self):
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
    
    def execute(self, ev=None):
        pass
    

class Plugin(BasePlugin):
    def __init__(self):
        pass

    def start(self, ev=None):
        pass

    def execute(self, ev=None):
        pass

    def stop(self, ev=None):
        pass
