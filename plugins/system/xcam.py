# Plugin
from enum import Enum, auto
from typing import List
from as64 import GameController, GameStatus, EventEmitter, config
from as64.as64 import GameEvent
from as64.constants import Event, Region
from as64.plugin import Plugin, Definition
from as64.state import State, StateMachine
from as64.utils import calculate_point_from_ratio

from as64 import api


from numpy import ndarray

import cv2


class XCamDefinition(Definition):
    NAME = "XCam Analyzer"
    VERSION = "1.0.0"


class XCam(Plugin):
    DEFINITION = XCamDefinition
    
    def __init__(self):
        super().__init__()
        
        self._state_machine: StateMachine = None
        
    def initialize(self, ev):
        emitter: EventEmitter = ev.emitter
        game: GameStatus = ev.status
        
        # Add an 'XCAM_CALIBRATED' event
        api.add_event_type('XCAM_CALIBRATED')
        
        # Calculate x-cam points
        p1 = calculate_point_from_ratio(game.region_rect(Region.XCAM)[2:], config.get('xcam', 'point_1_ratio'))
        p2 = calculate_point_from_ratio(game.region_rect(Region.XCAM)[2:], config.get('xcam', 'point_2_ratio'))
        
        print(p1, p2)
        
        # State Machine
        state_machine = StateMachine(event=ev)
        
        # States
        analyze_x_cam = AnalyzeXCamState(p1, p2)
        post_fade_out = XCamPostFadeoutState(p1, p2)
        
        # Transitions
        state_machine.add_transition(analyze_x_cam, post_fade_out, XCamSignal.PostFadeOut)
        state_machine.add_transition(post_fade_out, analyze_x_cam, XCamSignal.Analyze)
        
        # Set initial state
        state_machine.set_initial_state(analyze_x_cam)
        
        #
        self._state_machine = state_machine
        
        # Events
        emitter.on(Event.GAME_START, analyze_x_cam.calibrate) # Automatically calibrate x-cams when the intro ends
        emitter.on(Event.XCAM_CALIBRATED, post_fade_out.on_calibrate) # Update the post_fade_out x-cam values after a calibration has occured
        
        
    def execute(self, ev):
       self._state_machine.update()
       

class XCamSignal(Enum):
    Analyze = auto()
    PostFadeOut = auto()

def _in_x_cam(image: ndarray, point_1: List[int], point_2: List[int], colour_1: List[int], colour_2: List[int], threshold: float) -> bool:
    """Determines if the image is an 'x-cam' by analyzing two given points

    Args:
        image (ndarray): Image to analyze
        point_1 (List[int]): Test point 1
        point_2 (List[int]): Test point 2
        colour_1 (List[int]): Test point 1's target colour
        colour_2 (List[int]): Test point 2's target colour
        threshold (float): Max allowed variance in both positive and negative directions for a test points colour

    Returns:
        bool: Is image an 'x-cam'?
    """
    point_1_result = (colour_1[0] - threshold < image[point_1[1], point_1[0], 0] < colour_1[0] + threshold and
                      colour_1[1] - threshold < image[point_1[1], point_1[0], 1] < colour_1[1] + threshold and
                      colour_1[2] - threshold < image[point_1[1], point_1[0], 2] < colour_1[2] + threshold)
    
    point_2_result = (colour_2[0] - threshold < image[point_2[1], point_2[0], 0] < colour_2[0] + threshold and
                      colour_2[1] - threshold < image[point_2[1], point_2[0], 1] < colour_2[1] + threshold and
                      colour_2[2] - threshold < image[point_2[1], point_2[0], 2] < colour_2[2] + threshold)
    
    return point_1_result and point_2_result
    
class AnalyzeXCamState(State):
    def __init__(self, p1, p2):
        super().__init__()
        
        self._point_1 = p1
        self._point_2 = p2
        self._colour_1 = config.get('xcam', 'point_1_colour')
        self._colour_2 = config.get('xcam', 'point_2_colour')
        self._threshold = config.get('xcam', 'threshold')
        self._automatic_calibration = config.get('xcam', 'automatic_calibration')
        
    def calibrate(self, ev: GameEvent):
        """Automatically calibrates the x-cam settings given the current frame includes an x-cam.

        Args:
            ev (GameEvent): The current GameEvent
        """
        if not self._automatic_calibration:
            return
        
        emitter: EventEmitter = ev.emitter
        
        image = ev.status.get_region(Region.XCAM)
        
        self._colour_1 = image[self._point_1[1], self._point_1[0]]
        self._colour_2 = image[self._point_2[1], self._point_2[0]]
                
        config.set('xcam', 'point_1_colour', self._colour_1.tolist())
        config.set('xcam', 'point_2_colour', self._colour_2.tolist())
        
        config.save()
        
        emitter.emit(Event.XCAM_CALIBRATED)
        
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
        emitter: EventEmitter = ev.emitter
        
        # Get region
        x_cam_region = status.get_region(Region.XCAM)        
        
        # Analyze region
        in_x_cam = _in_x_cam(x_cam_region, self._point_1, self._point_2, self._colour_1, self._colour_2, self._threshold)
        
        if in_x_cam and not status.in_x_cam:
            print("X-Cam detected")
            status.x_cam_count += 1 if controller.count_x_cams else 0
            status.last_x_cam_time = status.current_time
            emitter.emit(Event.ENTER_XCAM)
            
        if not in_x_cam and status.in_x_cam:
            emitter.emit(Event.EXIT_XCAM)
            
        # Store value
        status.in_x_cam = in_x_cam
        
        # Handle edge cases of an x-cam occuring after a fade-out
        delta = status.current_time - status.last_fade_out_time
        if status.in_x_cam and 0.5 < delta < 2:
            sm.trigger(XCamSignal.PostFadeOut)
            
            
class XCamPostFadeoutState(State):
    def __init__(self, p1, p2):
        super().__init__()
        self._in_faded_x_cam = False
        
        self._point_1 = p1
        self._point_2 = p2
        self._colour_1 = config.get('xcam', 'point_1_colour')
        self._colour_2 = config.get('xcam', 'point_2_colour')
        self._threshold = config.get('xcam', 'threshold')
        
    def on_calibrate(self):
        self._colour_1 = config.get('xcam', 'point_1_colour')
        self._colour_2 = config.get('xcam', 'point_2_colour')

    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
        emitter: EventEmitter = ev.emitter
                
        # Get region
        x_cam_region = status.get_region(Region.XCAM)
        
        # Analyze region
        in_x_cam = _in_x_cam(x_cam_region, self._point_1, self._point_2, self._colour_1, self._colour_2, self._threshold)

        if not in_x_cam and status.in_x_cam and not self._in_faded_x_cam:
            duration = status.current_time - status.last_x_cam_time
            print("X-Cam Finished!", duration)

            # x-cam duration between 3 and 4 seconds indicates death
            if 3 < duration <= 4:
                status.fade_out_count = 0
                print("DEATH")
                if status.current_time - status.last_split_time < 6:
                    controller.undo()
                emitter.emit(Event.DEATH)
                sm.trigger(XCamSignal.Analyze)
            # x-cam duration between 4 and 5.5 seconds indicates in save menu
            elif 4 < duration < 5.5:
                self._in_faded_x_cam = True
                print("IN SAVE MENU")
                emitter.emit(Event.ENTER_SAVE_MENU)
            # x-cam duration greater than 7 seconds indicates a bowser fight
            elif duration > 7:
                print("IN BOWSER FIGHT")
                status.in_bowser_fight = True
                emitter.emit(Event.BOWSER_FIGHT)
                sm.trigger(XCamSignal.Analyze)
            else:
                sm.trigger(XCamSignal.Analyze)

        if self._in_faded_x_cam:
            status.in_x_cam = True
        else:
            status.in_x_cam = in_x_cam

        if in_x_cam and self._in_faded_x_cam:
            print("EXIT SAVE MENU")
            self._in_faded_x_cam = False
            emitter.emit(Event.EXIT_SAVE_MENU)
            sm.trigger(XCamSignal.Analyze)
            
