# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Transition:
    destination: 'State'
    condition: Optional[callable] = None

class State:
    """
    Represents a state within a state machine.
    """

    def __init__(self) -> None:
        self._transitions: Dict[Any, Transition] = {}
        self._parent: Optional['StateMachine'] = None

    def on_enter(self, sm: 'StateMachine', *args, **kwargs) -> None:
        """
        Called when entering the state.
        """
        pass

    def on_update(self, sm: 'StateMachine', *args, **kwargs) -> None:
        """
        Called to update the state.
        """
        pass

    def on_exit(self, sm: 'StateMachine', *args, **kwargs) -> None:
        """
        Called when exiting the state.
        """
        pass

    def _add_transition(self, destination: 'State', signal: Any, condition: Optional[callable] = None) -> None:
        if signal in self._transitions:
            raise ValueError(f"Transition for signal '{signal}' already exists in {self.__class__.__name__}.")
        self._transitions[signal] = Transition(destination, condition)

class StateMachine(State):
    """
    Represents a state machine which can contain multiple states and transitions.
    """

    def __init__(self) -> None:
        super().__init__()
        self._initial_state: Optional[State] = None
        self._current_state: Optional[State] = None
        self._states: List[State] = []
        self._global_transitions: Dict[Any, State] = {}
        self._has_started: bool = False

    def add_transition(self, source: Optional[State], destination: State, signal: Any, condition: Optional[callable] = None) -> None:
        """
        Adds a transition to the state machine.
        If source is None, it's a global transition.
        """
        if not isinstance(destination, State):
            raise TypeError("Destination must be an instance of State.")
        
        if source is not None and not isinstance(source, State):
            raise TypeError("Source must be an instance of State or None for global transitions.")
        
        if source and source not in self._states:
            self._add_state(source)
        if destination not in self._states:
            self._add_state(destination)
        
        if not source:
            if signal in self._global_transitions:
                raise ValueError(f"Global transition for signal '{signal}' already exists.")
            self._global_transitions[signal] = destination
            for state in self._states:
                if signal not in state._transitions:
                    state._add_transition(destination, signal)
        else:
            source._add_transition(destination, signal, condition)

    def _add_state(self, state: State) -> None:
        self._states.append(state)
        state._parent = self
        for signal, destination in self._global_transitions.items():
            if signal not in state._transitions:
                state._add_transition(destination, signal)

    def set_initial_state(self, state: State) -> None:
        """
        Sets the initial state of the state machine.
        """
        if state not in self._states:
            self._add_state(state)
        self._initial_state = state
        self._current_state = self._initial_state

    def trigger(self, signal: Any, *args, **kwargs) -> None:
        """
        Triggers a transition based on the given signal and event.
        """
        transition = self._current_state._transitions.get(signal) if self._current_state else None
        
        if not transition:
            if self._parent:
                self._parent.trigger(signal, *args, **kwargs)
            else:
                logger.warning(f"[trigger] Signal '{signal}' not handled and no parent to propagate to.")
            return

        if transition.condition and not transition.condition(*args, **kwargs):
            logger.debug(f"[trigger] Transition condition for signal '{signal}' not met.")
            return

        if transition.destination == self._current_state:
            logger.debug(f"[trigger] Ignoring internal transition for signal '{signal}'.")
            return

        logger.debug(
            "[trigger] Transition - Source: %s Destination: %s Signal: %s",
            self._current_state.__class__.__name__,
            transition.destination.__class__.__name__,
            signal
        )
        
        # Perform the transition
        self._current_state.on_exit(self, *args, **kwargs)
        self._current_state = transition.destination
        self._current_state.on_enter(self, *args, **kwargs)

    def update(self, *args, **kwargs) -> None:
        """
        Updates the current state.
        """
        if not self._has_started:
            if not self._initial_state:
                logger.error("[update] Initial state is not set. Cannot start the state machine.")
                return
            
            self._current_state = self._initial_state
            self._has_started = True
            
            logger.debug(f"[update] StateMachine initialized with initial state: {self._current_state.__class__.__name__}")
            
            self._current_state.on_enter(self, *args, **kwargs)

        if self._current_state:
            self._current_state.on_update(self, *args, **kwargs)

    def on_exit(self, sm: 'StateMachine', *args, **kwargs) -> None:
        """
        Called when exiting the state machine.
        """
        if self._current_state:
            self._current_state.on_exit(sm, *args, **kwargs)
        self._current_state = self._initial_state

    def on_update(self, sm: 'StateMachine', *args, **kwargs) -> None:
        """
        Called to update the state machine.
        """
        self.update(*args, **kwargs)
