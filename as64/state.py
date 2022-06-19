class State(object):
    def __init__(self):
        pass

    def on_enter(self):
        pass

    def on_update(self):
        pass

    def on_exit(self):
        pass


class Transition(object):
    def __init__(self):
        self._


class StateMachine(object):
    def __init__(self):
        self._initial_state: State = None
        self._current_state: State = None
        self._states: list = []

        self._transitions = {}

    def add_transition(source, destination, signal):
        pass



"""
--- STATE MACHINE PLANNING ---
    - Transition: Source, Destination, Signal

    - Source=None means signal will apply to ALL sources


"""
        



