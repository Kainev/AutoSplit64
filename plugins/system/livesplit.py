# Plugin
from as64.plugin import Plugin, Definition


class LiveSplitDefinition(Definition):
    NAME = "LiveSplit"
    VERSION = "1.0.0"


class LiveSplit(Plugin):
    DEFINITION = LiveSplitDefinition
        
    def execute(self, ev):
       pass
