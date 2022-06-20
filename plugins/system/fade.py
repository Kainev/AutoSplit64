# Plugin
from as64.plugin import Plugin, Definition


class FadeDefinition(Definition):
    NAME = "Fade Analyzer"
    VERSION = "1.0.0"


class Fade(Plugin):
    DEFINITION = FadeDefinition
        
    def execute(self, ev):
        pass
