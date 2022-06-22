# Plugin
from cmath import e
from time import time

import cv2
from as64 import config
from as64.as64 import AS64, GameController, GameStatus
from as64.constants import FadeStatus, Region, SplitType
from as64.plugin import Plugin, Definition

# Python
from enum import Enum, auto

from as64.state import StateMachine, State
from as64.utils import resource_path


class RTADefinition(Definition):
    NAME = "RTA"
    VERSION = "1.0.0"


class RTA(Plugin):
    DEFINITION = RTADefinition
    
    def __init__(self):
        super().__init__()
        
        self._state_machine: StateMachine = None
    
    def initialize(self, ev):
        state_machine = StateMachine(event=ev)
        
        # States
        intro = IntroStateMachine(ev)
        normal_split = NormalSplitStateMachine(ev)
        lblj_split = LBLJSplitStateMachine(ev)
        mips_split = MipsSplitStateMachine(ev)
        
        # Transitions
        # Addd intro state to main state machine (remove from normal), in execute have add if not in_intro to if check
        state_machine.add_transition(None, intro, AS64State.Intro)
        state_machine.add_transition(None, lblj_split, SplitType.LBLJ)
        state_machine.add_transition(None, normal_split, SplitType.STAR)
        state_machine.add_transition(None, mips_split, SplitType.MIPS)
        
        # Set initial state
        state_machine.set_initial_state(intro)
        
        #
        self._state_machine = state_machine
        
    def execute(self, ev):
        game: GameStatus = ev.status
        
        if not game.in_intro:
            self._state_machine.trigger(game.current_split.split_type)

        self._state_machine.update()
        
        
    
class AS64State(Enum):
    Intro = auto()
    InGame = auto()
    Fadeout = auto()
    Fadein = auto()   
    
    
class IntroStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
        self._initialize()
        
    def _initialize(self):
        # States
        intro = IntroState()
        fade_out = FadeoutState()
        
        # Transitions
        
        self.add_transition(intro, fade_out, AS64State.Fadeout)
        self.add_transition(fade_out, intro, AS64State.InGame)
        self.add_transition(fade_out, intro, AS64State.Intro)
        
        # Initial State
        self.set_initial_state(intro)
    
    
class NormalSplitStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
        self._initialize()
        
    def _initialize(self):
        # States
        intro = IntroState()
        in_game = InGameState()
        fade_out = FadeoutState()
        fade_in = FadeinState()
        
        # Transitions
        self.add_transition(None, in_game, AS64State.InGame)
        self.add_transition(None, fade_out, AS64State.Fadeout)
        self.add_transition(None, fade_in, AS64State.Fadein)
        
        # Initial State
        self.set_initial_state(in_game)
        
        
class MipsSplitStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
    
class LBLJSplitStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
        self._initialize()
    
    def _initialize(self):
        # States
        in_game = InGameState()
        fade_out = FadeoutLBLJState()
        
        self.add_transition(in_game, fade_out, AS64State.Fadeout)
        self.add_transition(fade_out, in_game, AS64State.InGame)
        self.add_transition(in_game, in_game, AS64State.Fadein)
        
        self.set_initial_state(in_game)
        

class BowserSplitStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
   
# ------------------------------------- STATES ------------------------------------------- #       
        
class IntroState(State):
    def __init__(self):
        super().__init__()
        
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 6
        controller.predict_star_count = True
        controller.count_x_cams = False
        controller.count_fades = False
        
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
                
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if game.star_count == game.route.initial_star:
            game.in_intro = False            

    
class InGameState(State):
    def __init__(self):
        super().__init__()
        
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 6
        controller.predict_star_count = True
        controller.count_x_cams = True
        controller.count_fades = True
        
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL:
            sm.trigger(AS64State.Fadeout)
        elif game.fade_status == FadeStatus.FADE_IN_PARTIAL:
            sm.trigger(AS64State.Fadein)
      
        
class BaseFadeoutState(State):
    def __init__(self):
        super().__init__()
        
        self._reset_template_1 = cv2.imread(resource_path(config.get('advanced', 'reset_frame_one')))
        self._reset_template_2 = cv2.imread(resource_path(config.get('advanced', 'reset_frame_two')))
        
        self._reset_threshold = config.get('thresholds', 'reset')
        self._undo_threshold = config.get('thresholds', 'undo')
                
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 29.97
        controller.predict_star_count = False
        controller.count_x_cams = True
        controller.count_fades = True
    
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        controller: GameController = ev.controller
        
        # Check if split should occur
        if self._should_split(game):
            controller.split()
        
        reset_region = game.get_region(Region.RESET)
        
        if cv2.minMaxLoc(cv2.matchTemplate(reset_region, self._reset_template_1, cv2.TM_SQDIFF_NORMED))[0] <= self._reset_threshold:
            self._reset(sm, game, controller)
        elif cv2.minMaxLoc(cv2.matchTemplate(reset_region, self._reset_template_2, cv2.TM_SQDIFF_NORMED))[0] <= self._reset_threshold:
            self._reset(sm, game, controller)
            
        if game.fade_status == FadeStatus.NO_FADE:
            sm.trigger(AS64State.InGame)

    def _reset(self, sm, game: GameStatus, controller: GameController):
        # Prevent the back-up reset from resetting again if first reset frame was detected
        if game.current_time - game.last_reset_time < 0.25:
            return
        
        # Record frame time reset occurred
        game.last_reset_time = game.current_time
        
        # Reset star_count
        game.star_count = None
        
        # Set in_intro
        game.in_intro = True
        
        # If a split occurred just before the reset, undo
        if game.current_time - game.last_split_time < self._undo_threshold:
            controller.undo()
            
        # Restart splits
        controller.reset()
        controller.split()

        sm.trigger(AS64State.Intro)
        
    def _should_split(self, game: GameStatus):
        return False
        
class FadeoutState(BaseFadeoutState):
    def __init__(self):
        super().__init__()
        
    def _should_split(self, game: GameStatus):
        if game.fade_status != FadeStatus.FADE_OUT_COMPLETE:
            return False    
        
        result = ((game.current_split.fadeout == game.fade_out_count or game.current_split.fadeout == -1) and
                  (game.current_split.fadein == game.fade_in_count or game.current_split.fadein == -1) and
                  (game.current_split.xcam == game.x_cam_count or game.current_split.xcam == -1) and
                  (game.current_split.star_count == game.star_count or game.current_split.star_count == -1))

        return result
    
class FadeoutLBLJState(BaseFadeoutState):
    def __init__(self):
        super().__init__()
        
    def _should_split(self, game: GameStatus):
        if game.fade_status != FadeStatus.FADE_OUT_COMPLETE:
            return False
        
        if game.current_time - game.x_cam_begin_time < 3:
            return False
        
        return game.current_split.star_count == game.star_count or game.current_split.star_count == -1
        

class FadeinState(State):
    def __init__(self):
        super().__init__()
                
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 29.97
        controller.predict_star_count = False
        
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        controller: GameController = ev.controller
        
        if game.fade_status == FadeStatus.NO_FADE:
            sm.trigger(AS64State.InGame)
        elif game.fade_status == FadeStatus.FADE_OUT_PARTIAL | FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)