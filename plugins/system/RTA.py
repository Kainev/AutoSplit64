# Plugin
from as64.plugin import Plugin, Definition


class RTADefinition(Definition):
    NAME = "RTA"
    VERSION = "1.0.0"


class RTA(Plugin):
    DEFINITION = RTADefinition
        
    def execute(self, ev):
        pass
      
        
