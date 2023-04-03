from as64.plugin import Plugin, Definition

from PySide6.QtWidgets import QWidget


class SplitNotesDefinition(Definition):
    NAME = "Split Notes"
    VERSION = "0.1.0"
    AUTHOR = "Synozure"
    EXECUTION = Definition.Execution.FRAME


class SplitNotes(Plugin):
    DEFINITION = SplitNotesDefinition

    def __init__(self):
        super().__init__()

    def initialize(self, ev=None):
        pass

    def execute(self, ev=None):
        print("EXC!")
