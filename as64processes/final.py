import time

import cv2
import numpy as np

import as64core

from as64core import config
from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessFinalStageEntry(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("ENTERED")
        self.register_signal("FADEOUT")
        self.bowser_lower_bound = config.get("split_final_star", "stage_lower_bound")
        self.bowser_upper_bound = config.get("split_final_star", "stage_upper_bound")

    def execute(self):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        lower = np.array(self.bowser_lower_bound, dtype="uint8")
        upper = np.array(self.bowser_upper_bound, dtype="uint8")

        star_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=star_mask)

        if not is_black(output, 0.1, 0.9):
            return self.signals["ENTERED"]
        else:
            return self.signals["LOOP"]

    def on_transition(self):
        print("PROCESS FINAL STAGE ENTRY")

        as64core.fps = 10

        super().on_transition()


class ProcessFinalStarSpawn(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("SPAWNED")
        self.register_signal("FADEOUT")
        self._iteration_value = {0: 1, 1: 4, 2: 1}
        self._looping_iteration = 0

        self.star_lower_bound = config.get("split_final_star", "star_lower_bound")
        self.star_upper_bound = config.get("split_final_star", "star_upper_bound")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if self._star_visible() and self.loop_time() > 30:
            if self._looping_iteration == len(self._iteration_value):
                print("spawned :)")
                return self.signals["SPAWNED"]
            else:
                try:
                    print("iter", self._looping_iteration)
                    time.sleep(self._iteration_value[self._looping_iteration])
                except IndexError:
                    pass

            self._looping_iteration += 1

            return self.signals["LOOP"]
        else:
            self._looping_iteration = 0

        return self.signals["LOOP"]

    def on_transition(self):
        print("PROCESS FINAL STAR SPAWN")
        as64core.fps = 29.97
        self._looping_iteration = 0

        super().on_transition()

    def _star_visible(self, threshold=0.999):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        lower = np.array(self.star_lower_bound, dtype="uint8")
        upper = np.array(self.star_upper_bound, dtype="uint8")

        star_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=star_mask)

        return not is_black(output, 0.1, threshold)


class ProcessFinalStarGrab(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("COMPLETE")
        self.register_signal("FADEOUT")
        self.star_lower_bound = config.get("split_final_star", "star_lower_bound")
        self.star_upper_bound = config.get("split_final_star", "star_upper_bound")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if not self._star_visible():
            print("Grabbed!")
            as64core.split()
            return self.signals["COMPLETE"]

        return self.signals["LOOP"]

    def on_transition(self):
        print("PROCESS FINAL STAR GRAB")

        as64core.fps = 29.97

        super().on_transition()

    def _star_visible(self, threshold=0.999):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        lower = np.array(self.star_lower_bound, dtype="uint8")
        upper = np.array(self.star_upper_bound, dtype="uint8")

        star_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=star_mask)

        return not is_black(output, 0.1, threshold)
