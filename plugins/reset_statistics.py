from as64.plugin import Plugin, Definition

from as64 import EventEmitter, GameStatus
from as64.constants import Event


class ResetStatisticsDefinition(Definition):
    NAME = "Reset Statistics"
    VERSION = "0.1.0"
    AUTHOR = "Synozure"
    EXECUTION = Definition.Execution.EVENT_ONLY


class ResetStatistics(Plugin):
    DEFINITION = ResetStatisticsDefinition

    def __init__(self):
        super().__init__()

        self._current_star = None
        self._game_status: GameStatus = None

        self._tracker = {}

        for star in range(0, 121):
            self._tracker[star] = 0

    def start(self, ev=None):
        self._game_status: GameStatus = ev.status

        emitter: EventEmitter = ev.emitter
        emitter.on(Event.STAR_COLLECTED, self._on_star_collected)
        emitter.on(Event.RESET, self._on_reset)

    def stop(self, ev=None):
        self._current_star = None
        self._game_status = None

    def _on_star_collected(self, star):
        self._current_star = star

    def _on_reset(self):
        self._tracker[self._current_star] += 1

