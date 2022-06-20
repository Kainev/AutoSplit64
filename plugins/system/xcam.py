# Plugin
from as64.plugin import Plugin, Definition


class XCamDefinition(Definition):
    NAME = "XCam Analyzer"
    VERSION = "1.0.0"


class XCam(Plugin):
    DEFINITION = XCamDefinition
        
    def execute(self, ev):
        pass
