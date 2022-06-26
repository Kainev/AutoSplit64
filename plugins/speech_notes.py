from as64.plugin import Plugin, Definition

import threading

import pyttsx3
import toml

from as64.constants import Event

class SpeechNotesDefinition(Definition):
    NAME = "Speech Notes"
    VERSION = "0.1.0"

class SpeechNotes(Plugin):
    DEFINITION = SpeechNotesDefinition
    
    def __init__(self):
        super().__init__()
        
        self._engine = None
        self._notes = None
        
    def initialize(self):
        self._engine = pyttsx3.init()
        self._notes = toml.load('speech_notes.txt')
        
    def start(self, ev):
        ev.emitter.on(Event.STAR_COLLECTED, self.on_star_collected)
        
    def on_star_collected(self, star_count):
        threading.Thread(target=self.speak, args=(str(star_count),)).start()
        
    def speak(self, star_count):
        if star_count in self._notes:
            self._engine.say(self._notes[star_count])
            self._engine.runAndWait()


# import pyttsx3

# engine = pyttsx3.init()
# engine.say("Nuitka")
# engine.runAndWait()
