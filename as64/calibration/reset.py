# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import time
import threading
import logging

import cv2
import numpy as np

from as64 import api
from as64 import config
from as64.enums import Version, Region
from as64.core.capture import GameCapture

from as64.plugins.management import plugin_manager

logger = logging.getLogger(__name__)

class ResetCalibration:
    def __init__(self, enqueue_message, capture_plugin):
        self._enqueue = enqueue_message
        self._capture = GameCapture(Version.JP, config.get("capture", "region"), capture_plugin)
        
        self._black_lower_bound = np.array(config.get("colour_bounds", "black_lower_bound"), dtype='uint8')
        self._black_upper_bound = np.array(config.get("colour_bounds", "black_upper_bound"), dtype='uint8')
        self._black_threshold = config.get("thresholds", "black")
        
        self._capture_count = 5
        self._fps = 29.97

    def run(self, stop_event):
        reset_occurred = False
        frame = 0
        captured_frames = []
        
        while not stop_event.is_set():
            c_time = time.perf_counter()
            
            try:
                self._capture.capture()
            except:
                self._enqueue({"event": "error", "data": f"Unable to capture {config.get("capture", "source")}"})
                stop_event.set()
                break
            
            reset_region = self._capture.region_image(Region.RESET)
            life_region = self._capture.region_image(Region.LIFE)
            fade_region = self._capture.region_image(Region.FADEOUT)
                        
            in_fade = api.image.in_colour_range(life_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold)
            fade_complete = api.image.in_colour_range(fade_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold)
            
            if in_fade and fade_complete:
                reset_occurred = True
                
            if reset_occurred:
                if not api.image.in_colour_range(fade_region, self._black_lower_bound, self._black_upper_bound, self._black_threshold):
                    frame += 1
                    
                    if frame <= self._capture_count:
                        captured_frames.append(reset_region)
                    else:
                        stop_event.set()
                        break
                    
            try:
                time.sleep((1 / self._fps) - (time.perf_counter() - c_time))
            except ValueError:
                pass
            
            
        if len(captured_frames) != self._capture_count:
            return
        
        for i, frame in enumerate(captured_frames):
            cv2.imwrite(f"templates/generated_temp_{i + 1}.jpg", frame)
            
        self._enqueue({"event": "calibration.reset_detection.generated"})
            
    
    def stop(self):
        pass
    
    def apply(self, index_one, index_two):
        source_1 = f"templates/generated_temp_{index_one + 1}.jpg"
        source_2 = f"templates/generated_temp_{index_two + 1}.jpg"
        dest_1 = "templates/generated_reset_one.jpg"
        dest_2 = "templates/generated_reset_two.jpg"
        
        try:
            os.replace(source_1, dest_1)
            os.replace(source_2, dest_2)
            self._enqueue({"event": "calibration.reset_detection.applied"})
            
            return True
        except Exception as e:
            logger.exception("[apply] Failed to apply reset templates")
            self._enqueue({"event": "error", "data": f"Failed to apply reset templates\n {str(e)}"})
            
            return False
    
    def clean(self):
        for i in range(self._capture_count):
            try:
                os.remove(f"templates/generated_temp_{i + 1}.jpg")
            except FileNotFoundError:
                pass
            


_reset_thread = None
_reset_stop_event = None
_reset_instance = None


@api.rpc.register("calibration.reset_detection.start")
def start():
    global _reset_thread, _reset_stop_event, _reset_instance
    
    if _reset_thread is not None and _reset_thread.is_alive():
        return
    
    capture_plugin = plugin_manager.get_active_plugin_classes(api.CapturePlugin)()
    
    _reset_stop_event = threading.Event()
    _reset_instance = ResetCalibration(api.ipc.enqueue_ui_message, capture_plugin)
    
    _reset_thread = threading.Thread(
        target=_reset_instance.run,
        args=(_reset_stop_event,),
        daemon=True
    )
    
    _reset_thread.start()

@api.rpc.register("calibration.reset_detection.stop")
def stop():
    global _reset_thread, _reset_stop_event, _reset_instance
    
    if _reset_stop_event is not None:
        _reset_stop_event.set()
        
    if _reset_thread is not None:
        _reset_thread.join(timeout=2)
        
    if _reset_instance is not None:
        _reset_instance.clean()
    
    _reset_thread = None
    _reset_stop_event = None
    _reset_instance = None


@api.rpc.register("calibration.reset_detection.apply")
def apply(index_one, index_two):
    global _reset_instance
    
    if _reset_instance is not None:
        return _reset_instance.apply(index_one, index_two)