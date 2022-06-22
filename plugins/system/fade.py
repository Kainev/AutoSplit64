# Plugin
from enum import Enum, auto
import numpy as np
from as64 import GameController, GameStatus, config
from as64.image import in_colour_range
from as64.plugin import Plugin, Definition
from as64.state import State, StateMachine
from as64.constants import FadeStatus, Region


class FadeDefinition(Definition):
    NAME = "Fade Analyzer"
    VERSION = "1.0.0"


class Fade(Plugin):
    DEFINITION = FadeDefinition
    
    def __init__(self):
        super().__init__()
        
        self._state_machine: StateMachine = None
        
    def initialize(self, ev):
        state_machine = StateMachine(event=ev)
        
        # States
        wait_for_fade = WaitForFadeState()
        partial_fade_out = PartialFadeOutState()
        partial_fade_in = PartialFadeInState()
        fade_out_complete = FadeOutCompleteState()
        fade_in_complete = FadeInCompleteState()
        
        # Transitions
        state_machine.add_transition(None, wait_for_fade, FadeSignal.WaitForFade)
        
        state_machine.add_transition(wait_for_fade, partial_fade_out, FadeSignal.PartialFadeOut)
        state_machine.add_transition(partial_fade_out, fade_out_complete, FadeSignal.FadeOutComplete)
        
        state_machine.add_transition(wait_for_fade, partial_fade_in, FadeSignal.PartialFadeIn)
        state_machine.add_transition(partial_fade_in, fade_in_complete, FadeSignal.FadeInComplete)
                
        # Set initial state
        state_machine.set_initial_state(wait_for_fade)
        
        #
        self._state_machine = state_machine
        
    def execute(self, ev):
        self._state_machine.update()
    
    
class FadeSignal(Enum):
    WaitForFade = auto()
    PartialFadeOut = auto()
    PartialFadeIn = auto()
    FadeOutComplete = auto()
    FadeInComplete = auto()
       
    
class FadeStateBase(State):
    def __init__(self):
        super().__init__()
        
        self._black_lower_bound = np.array(config.get("colour_bounds", "black_lower_bound"), dtype='uint8')
        self._black_upper_bound = np.array(config.get("colour_bounds", "black_upper_bound"), dtype='uint8')
        self._white_lower_bound = np.array(config.get("colour_bounds", "white_lower_bound"), dtype='uint8')
        self._white_upper_bound = np.array(config.get("colour_bounds", "white_upper_bound"), dtype='uint8')
        
        self._black_threshold = config.get("thresholds", "black")
        self._white_threshold = config.get("thresholds", "white")
        
        
class WaitForFadeState(FadeStateBase):
    def __init__(self):
        super().__init__()
                
    def on_update(self, sm, ev):
        controller: GameController = ev.controller
        status: GameStatus = ev.status
        
        life_region = status.get_region(Region.LIFE)
        
        if in_colour_range(life_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold):
            WaitForFadeState._on_fade_out_detected(sm, status, controller)
        elif in_colour_range(life_region, self._white_lower_bound, self._white_upper_bound, self._white_threshold):
            WaitForFadeState._on_fade_in_detected(sm, status, controller)
    
    @staticmethod
    def _on_fade_out_detected(sm: StateMachine, status: GameStatus, controller: GameController):
        status.fade_status = FadeStatus.FADE_OUT_PARTIAL
        status.in_bowser_fight = False
        status.fade_out_count += 1 if controller.count_fades else 0
        
        # Reset x-cam count
        status.x_cam_count = 0
        
        # Record time fade out began
        status.last_fade_out_time = status.current_time
        
        # Transition State
        sm.trigger(FadeSignal.PartialFadeOut)

    @staticmethod
    def _on_fade_in_detected(sm: StateMachine, status: GameStatus, controller: GameController):
        status.fade_status = FadeStatus.FADE_IN_PARTIAL
        status.in_bowser_fight = False
        status.fade_in_count += 1 if controller.count_fades else 0
        
        # Reset x-cam count
        status.x_cam_count = 0
        
        # Record time fade out began
        status.last_fade_in_time = status.current_time
        
        # Transition State
        sm.trigger(FadeSignal.PartialFadeIn)
        

class PartialFadeOutState(FadeStateBase):
    def __init__(self):
        super().__init__()
        
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        
        fadeout_region = status.get_region(Region.FADEOUT)
        
        if in_colour_range(fadeout_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold):
            status.fade_status = FadeStatus.FADE_OUT_COMPLETE
            sm.trigger(FadeSignal.FadeOutComplete)
            
            
class PartialFadeInState(FadeStateBase):
    def __init__(self):
        super().__init__()
        
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        
        fadein_region = status.get_region(Region.FADEIN)
        
        if not in_colour_range(fadein_region, self._white_lower_bound, self._white_upper_bound, self._white_threshold):
            status.fade_status = FadeStatus.FADE_IN_COMPLETE
            sm.trigger(FadeSignal.FadeInComplete)
            
            
class FadeOutCompleteState(FadeStateBase):
    def __init__(self):
        super().__init__()
                
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        
        life_region = status.get_region(Region.LIFE)
        
        if not in_colour_range(life_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold):
            status.fade_status = FadeStatus.NO_FADE
            sm.trigger(FadeSignal.WaitForFade)
            
            
class FadeInCompleteState(FadeStateBase):
    def __init__(self):
        super().__init__()
                
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        
        life_region = status.get_region(Region.LIFE)
        
        if not in_colour_range(life_region, self._white_lower_bound, self._white_upper_bound, self._white_threshold):
            status.fade_status = FadeStatus.NO_FADE
            sm.trigger(FadeSignal.WaitForFade)
