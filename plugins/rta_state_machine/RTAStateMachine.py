from as64.plugin import Plugin, Definition


class RTAStateMachineDefinition(Definition):
    NAME = "RTA State Machine"
    VERSION = "0.1.0"

    SCHEDULE = Definition.Schedule.FRAME
    SETTINGS = {
        
    }


class RTAStateMachine(Plugin):
    DEFINITION = RTAStateMachineDefinition

    def initialize(self):
        pass

    def execute(self, ev):
        pass