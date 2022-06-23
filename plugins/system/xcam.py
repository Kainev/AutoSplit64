# Plugin
from enum import Enum, auto
from as64.as64 import GameController, GameStatus
from as64.constants import Region
from as64.plugin import Plugin, Definition
from as64.state import State, StateMachine

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
        state_machine = StateMachine(event=ev)
        
        # States
        analyze_x_cam = AnalyzeXCamState()
        post_fade_out = XCamPostFadeoutState()
        
        # Transitions
        state_machine.add_transition(analyze_x_cam, post_fade_out, XCamSignal.PostFadeOut)
        state_machine.add_transition(post_fade_out, analyze_x_cam, XCamSignal.Analyze)
        
        # Set initial state
        state_machine.set_initial_state(analyze_x_cam)
        
        #
        self._state_machine = state_machine
        
    def execute(self, ev):
       self._state_machine.update()
       

class XCamSignal(Enum):
    Analyze = auto()
    PostFadeOut = auto()

def _in_x_cam(image):
    threshold = 25

    colour_1 = [3, 10, 118]
    colour_2 = [40, 52, 151]
    
    point_1 = [18, 8]
    point_2 = [18, 18]  

    point_1_result = (colour_1[0] - threshold < image[point_1[0], point_1[1], 0] < colour_1[0] + threshold and
                      colour_1[1] - threshold < image[point_1[0], point_1[1], 1] < colour_1[1] + threshold and
                      colour_1[2] - threshold < image[point_1[0], point_1[1], 2] < colour_1[2] + threshold)
    
    point_2_result = (colour_2[0] - threshold < image[point_2[0], point_2[1], 0] < colour_2[0] + threshold and
                      colour_2[1] - threshold < image[point_2[0], point_2[1], 1] < colour_2[1] + threshold and
                      colour_2[2] - threshold < image[point_2[0], point_2[1], 2] < colour_2[2] + threshold)

    return point_1_result and point_2_result
    
class AnalyzeXCamState(State):
    def __init__(self):
        super().__init__()
        
    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
        
        # Get region
        x_cam_region = status.get_region(Region.XCAM)        
        
        # Analyze region
        in_x_cam = _in_x_cam(x_cam_region)
        
        if in_x_cam and not status.in_x_cam:
            status.x_cam_count += 1 if controller.count_x_cams else 0
            status.x_cam_begin_time = status.current_time
            print("X-Cam Detected")
            
        # Store value
        status.in_x_cam = in_x_cam
        
        # Handle edge cases of an x-cam occuring after a fade-out
        delta = status.current_time - status.last_fade_out_time
        if status.in_x_cam and 0.5 < delta < 2:
            sm.trigger(XCamSignal.PostFadeOut)
            
            
class XCamPostFadeoutState(State):
    def __init__(self):
        super().__init__()
        self._in_faded_x_cam = False

    def on_update(self, sm, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
                
        # Get region
        x_cam_region = status.get_region(Region.XCAM)
        
        # Analyze region
        in_x_cam = _in_x_cam(x_cam_region)

        if not in_x_cam and status.in_x_cam and not self._in_faded_x_cam:
            duration = status.current_time - status.x_cam_begin_time
            print("X-Cam Finished!", duration)

            # x-cam duration between 3 and 4 seconds indicates death
            if 3 < duration <= 4:
                status.fade_out_count = 0
                print("DEATH")
                if status.current_time - status.last_split_time < 6:
                    controller.undo()
                sm.trigger(XCamSignal.Analyze)
            # x-cam duration between 4 and 5.5 seconds indicates in save menu
            elif 4 < duration < 5.5:
                self._in_faded_x_cam = True
                print("IN SAVE MENU")
            # x-cam duration greater than 7 seconds indicates a bowser fight
            elif duration > 7:
                print("IN BOWSER FIGHT")
                status.in_bowser_fight = True
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
            sm.trigger(XCamSignal.Analyze)
