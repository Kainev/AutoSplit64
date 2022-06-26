from as64.plugin import Plugin, Definition

from enum import Enum, auto

import cv2
import numpy as np

from as64 import GameController, GameStatus, EventEmitter, config
from as64.constants import FadeStatus, Region, SplitType, Event
from as64.state import StateMachine, State
from as64.utils import resource_path
from as64.image import in_colour_range


class RTADefinition(Definition):
    NAME = "RTA"
    VERSION = "1.0.0"


class RTA(Plugin):
    DEFINITION = RTADefinition
    
    def __init__(self):
        super().__init__()
        
        self._state_machine: StateMachine = None
        self._game_status: GameStatus = None
    
    def initialize(self, ev):
        self._game_status: GameStatus = ev.status
        state_machine = StateMachine(event=ev)
        
        # States
        intro = IntroStateMachine(ev)
        normal_split = NormalSplitStateMachine(ev)
        lblj_split = LBLJSplitStateMachine(ev)
        mips_split = MipsSplitStateMachine(ev)
        bowser_split = BowserSplitStateMachine(ev)
        
        # Transitions
        # Addd intro state to main state machine (remove from normal), in execute have add if not in_intro to if check
        state_machine.add_transition(None, intro, AS64State.Intro)
        state_machine.add_transition(None, lblj_split, SplitType.LBLJ)
        state_machine.add_transition(None, normal_split, SplitType.STAR)
        state_machine.add_transition(None, mips_split, SplitType.MIPS)
        state_machine.add_transition(None, bowser_split, SplitType.BOWSER)
        
        # Set initial state
        state_machine.set_initial_state(intro)
        
        #
        self._state_machine = state_machine
        
        # Register event callbacks
        ev.emitter.on(Event.EXTERNAL_SPLIT_UPDATE, self.on_external_split_update)
        
    
    def on_external_split_update(self):
        print("External Split Update!")
        self._state_machine.trigger(self._game_status.current_split.split_type)
        
    def execute(self, ev):
        self._state_machine.update()
        
        
class AS64State(Enum):
    Intro = auto()
    InGame = auto()
    Fadeout = auto()
    Fadein = auto()
    WaitForBowser = auto()
    Key = auto()
    PostKey = auto()
    Final = auto()
    
    
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
        emitter: EventEmitter = ev.emitter
                
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if game.star_count == game.route.initial_star:
            game.in_intro = False
            emitter.emit(Event.GAME_START, ev)
            sm.trigger(game.current_split.split_type)
        # TODO: If current star prediction contained within split, jump to star
        # elif game.

    
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
        if self.should_split(game):
            self.handle_split(sm, game, controller)
        
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
        
    def should_split(self, game: GameStatus):
        return False
    
    def handle_split(self, sm, game: GameStatus, controller: GameController):
        controller.split()
        # TODO: Catch index exception?
        sm.trigger(game.route.splits[game.current_split_index + 1].split_type)
        
  
class FadeoutState(BaseFadeoutState):
    def __init__(self):
        super().__init__()
        
        # TODO: Add to config
        self._minimum_split_delay = 0.6
        
    def should_split(self, game: GameStatus):
        if game.fade_status != FadeStatus.FADE_OUT_COMPLETE:
            return False
        
        if game.current_time - game.last_fade_out_time < self._minimum_split_delay:
            return False    
        
        result = ((game.current_split.fadeout == game.fade_out_count or game.current_split.fadeout == -1) and
                  (game.current_split.fadein == game.fade_in_count or game.current_split.fadein == -1) and
                  (game.current_split.xcam == game.x_cam_count or game.current_split.xcam == -1) and
                  (game.current_split.star_count == game.star_count or game.current_split.star_count == -1))

        return result
 
    
class FadeoutLBLJState(BaseFadeoutState):
    def __init__(self):
        super().__init__()
        
        # TODO: Add to config
        self._minimum_split_delay = 0.53
        
    def should_split(self, game: GameStatus):
        if game.fade_status != FadeStatus.FADE_OUT_COMPLETE:
            return False
        
        if game.current_time - game.last_x_cam_time < 3:
            return False
        
        if game.current_time - game.last_fade_out_time < self._minimum_split_delay:
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



class BowserSplitStateMachine(StateMachine):
    def __init__(self, ev):
        super().__init__(ev)
        
        self._initialize()
        
    def _initialize(self):
        # States
        wait_for_bowser = WaitForBowserState()
        base_fadeout = BaseFadeoutState()
        key_split = KeySplitState()
        key_fade_out = KeyFadeoutState()
        post_key = PostKeyState()
        
        final_bowser = FinalBowserState()
        final_star = FinalStarState()
        wait_for_reset = WaitForReset()
        wait_for_reset_fadeout = BaseFadeoutState()
        
        # Transitions 
        self.add_transition(base_fadeout, wait_for_bowser, AS64State.InGame)
        self.add_transition(wait_for_bowser, base_fadeout, AS64State.Fadeout)
        self.add_transition(wait_for_bowser, key_split, AS64State.Key)
        self.add_transition(wait_for_bowser, final_bowser, AS64State.Final)
        
        self.add_transition(key_split, key_fade_out, AS64State.Fadeout)
        self.add_transition(key_fade_out, post_key, AS64State.InGame)
        
        self.add_transition(post_key, wait_for_bowser, AS64State.WaitForBowser)
        self.add_transition(post_key, base_fadeout, AS64State.Fadeout)
        
        self.add_transition(final_bowser, final_star, AS64State.Final)
        self.add_transition(final_bowser, base_fadeout, AS64State.Fadeout)
        
        self.add_transition(final_star, base_fadeout, AS64State.Fadeout)
        self.add_transition(final_star, wait_for_reset, AS64State.Final)
        
        self.add_transition(wait_for_reset, wait_for_reset_fadeout, AS64State.Fadeout)
        self.add_transition(wait_for_reset_fadeout, wait_for_reset, AS64State.InGame)
        
        
        # Set initial state
        self.set_initial_state(wait_for_bowser)


class WaitForBowserState(State):
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
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if game.in_bowser_fight:
            if game.current_split_index != len(game.route.splits) - 1:
                sm.trigger(AS64State.Key)
            else:
                sm.trigger(AS64State.Final)
                
                
class KeySplitState(State):
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
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        

class KeyFadeoutState(BaseFadeoutState):
    def __init__(self):
        super().__init__()
        
    def should_split(self, game: GameStatus):
        if game.fade_status != FadeStatus.FADE_OUT_COMPLETE:
            return False
        
        if game.current_time - game.last_x_cam_time > 4:
            return False
        
        return game.current_split.split_type == SplitType.BOWSER
    
    def handle_split(self, sm, game: GameStatus, controller: GameController):
        controller.split()
        

class PostKeyState(State):
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
        controller: GameController = ev.controller
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if not game.in_x_cam:
            controller.undo()
            sm.trigger(AS64State.WaitForBowser)
            return
        
        # TODO: Catch index exception?
        sm.trigger(game.route.splits[game.current_split_index + 1].split_type)
            

class FinalBowserState(State):
    def __init__(self):
        super().__init__()
        
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 6
        controller.predict_star_count = False
        controller.count_x_cams = True
        controller.count_fades = True
                
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if game.in_x_cam:
            sm.trigger(AS64State.Final)
            

class FinalStarState(State):
    def __init__(self):
        super().__init__()

        self._white_lower_bound = np.array(config.get('colour_bounds', 'white_lower_bound'), dtype='uint8')
        self._white_upper_bound = np.array(config.get('colour_bounds', 'white_upper_bound'), dtype='uint8')
        self._final_star_threshold = config.get('thresholds', 'final_star')
        
        self.index = 0
        
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 29.97
        controller.predict_star_count = False
        controller.count_x_cams = True
        controller.count_fades = True
                
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        controller: GameController = ev.controller
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            return
        
        if not game.in_x_cam:
            final_region = game.get_region(Region.FINAL_STAR)
            
            if in_colour_range(final_region, self._white_lower_bound, self._white_upper_bound, self._final_star_threshold):
                controller.split()            
                sm.trigger(AS64State.Final)
            
            
class WaitForReset(State):
    def __init__(self):
        super().__init__()
        
    def on_enter(self, sm, ev):
        controller: GameController = ev.controller
        
        controller.fps = 6
        controller.predict_star_count = False
        controller.count_x_cams = False
        controller.count_fades = False
                
    def on_update(self, sm, ev):
        game: GameStatus = ev.status
        
        if game.fade_status == FadeStatus.FADE_OUT_PARTIAL or game.fade_status == FadeStatus.FADE_OUT_COMPLETE:
            sm.trigger(AS64State.Fadeout)
            
         