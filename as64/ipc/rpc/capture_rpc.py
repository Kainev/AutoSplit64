# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import cv2

from as64.plugins import CapturePlugin
from as64.plugins.management import plugin_manager

from .registry import register


@register("save_frame")
def save_frame():
    capture_plugin = plugin_manager.get_active_plugin_classes(CapturePlugin)()
    
    frame = capture_plugin.capture()
    cv2.imwrite("resources/capture.jpg", frame)
    
