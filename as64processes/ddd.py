import cv2
import numpy as np

import as64core

from as64core import config
from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessFindDDDPortal(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("FOUND")
        self.register_signal("FADEOUT")
        self.portal_lower_bound = config.get("split_ddd_enter", "portal_lower_bound")
        self.portal_upper_bound = config.get("split_ddd_enter", "portal_upper_bound")

    def execute(self):
        no_hud = as64core.get_region(as64core.GAME_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        lower = np.array(self.portal_lower_bound, dtype="uint8")
        upper = np.array(self.portal_upper_bound, dtype="uint8")

        portal_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)

        if not is_black(output, 0.1, 0.99):
            return self.signals["FOUND"]
        else:
            return self.signals["LOOP"]

    def on_transition(self):
        print("PROCESS FIND DDD PORTAL")
        as64core.fps = 10

        super().on_transition()


class ProcessDDDEntry(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("ENTERED")
        self.register_signal("FADEOUT")
        self.lower_bound = np.array(config.get("split_ddd_enter", "hat_lower_bound"), dtype="uint8")
        self.upper_bound = np.array(config.get("split_ddd_enter", "hat_upper_bound"), dtype="uint8")

    def execute(self):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if not cv2.inRange(no_hud, self.lower_bound, self.upper_bound).any():
            as64core.split()
            return self.signals["ENTERED"]
        else:
            return self.signals["LOOP"]

    def on_transition(self):
        #
        print("PROCESS DDD ENTRY")
        as64core.fps = 10

        super().on_transition()
