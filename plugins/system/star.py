# Plugin
from as64.plugin import Plugin, Definition


class StarDefinition(Definition):
    NAME = "Star Analyzer"
    VERSION = "1.0.0"


class Star(Plugin):
    DEFINITION = StarDefinition
        
    def execute(self, ev):
        pass
