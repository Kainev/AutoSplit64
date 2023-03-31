from typing import Any, Dict, List


class State(object):
    def __init__(self):
        self._transitions: Dict[Any: State] = {}
        self._parent: StateMachine = None

    def on_enter(self, sm, ev):
        try:
            self._current_state.on_enter(sm, ev)
        except AttributeError:
            pass

    def on_update(self, sm, ev):
        pass

    def on_exit(self, sm, ev):
        pass
          
    def _add_transition(self, destination, signal: Any):
        self._transitions[signal] = destination


class StateMachine(State):
    def __init__(self, event):
        super().__init__()
        
        self._initial_state: State = None
        self._current_state: State = None
        self._states: list[State] = []
        
        self._event = event
        
        self._global_transitions = {}

    def add_transition(self, source: State, destination: State, signal: Any):
        # Register states with StateMachine
        if source and source not in self._states:
            self._add_state(source)
        if destination not in self._states:
            self._add_state(destination)
        
        # If no source state is provided, add as global transition        
        if not source:
            # TODO: Throw error if signal is already a global transition
            self._global_transitions[signal] = destination
            
            for state in self._states:
                if signal not in state._transitions.keys():
                    state._add_transition(destination, signal)
        else:
            source._add_transition(destination, signal)
          
    def _add_state(self, state: State):
        self._states.append(state)
        state._parent = self
        
        for transition in self._global_transitions:
            state._add_transition(self._global_transitions[transition], transition)
                       
    def set_initial_state(self, state: State):
        # Ensure state is registered
        if state not in self._states:
            self._add_state(state)
            
        # Set initial state
        self._initial_state = state
        
        # On first call, set current state to initial state
        if not self._current_state:
            self._current_state = self._initial_state
            
    def trigger(self, signal: Any):
        # Propagate signal up if not caught
        if signal not in self._current_state._transitions:
                self._parent.trigger(signal)
                return
 
        # Ignore internal transitions
        if self._current_state._transitions[signal] == self._current_state:
            return
    
        print("Transition - Source: {} Destination: {}".format(self._current_state.__class__.__name__, self._current_state._transitions[signal].__class__.__name__))
        
        # Transition to new state
        self._current_state.on_exit(self, self._event)
        self._current_state: State = self._current_state._transitions[signal]
        self._current_state.on_enter(self, self._event)
        
    def update(self):
        self._current_state.on_update(self, self._event)
        # print(self._current_state)

    def on_exit(self, sm, ev):
        self._current_state.on_exit(self, self._event)
        self._current_state = self._initial_state
        
    def on_update(self, sm, ev):
        self.update()
        
        
    


"""
--- STATE MACHINE PLANNING ---
    - Transition: Source, Destination, Signal

    - Source=None means signal will apply to ALL sources


"""
        



