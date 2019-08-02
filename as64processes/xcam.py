import cv2
import numpy as np
import time

import as64core

from as64core.image_utils import is_black
from as64core.processing import Process


class ProcessXCam(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("FADEOUT")
        self.register_signal("FADEIN")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        #if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            #return self.signals["FADEIN"]

        if as64core.incoming_split():
            if as64core.xcam_count == 0 and as64core.in_xcam and as64core.current_time - as64core.collection_time < 1:
                as64core.split()
            elif as64core.xcam_count == as64core.current_split().on_xcam:
                as64core.xcam_count = 0
                as64core.split()

        return self.signals["LOOP"]

    def on_transition(self):
        as64core.fps = 29.97
        as64core.enable_predictions(True)
        as64core.enable_xcam_count(True)

        super().on_transition()


class ProcessXCamStartUpSegment(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("FADEOUT")
        self.register_signal("START")
        self.lower_bound = [0, 0, 50]
        self.upper_bound = [30, 40, 200]

        self._predictions = True

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if as64core.fadeout_count == 1:
            as64core.fps = 29.97
            as64core.enable_predictions(not self._predictions)
            xcam = as64core.get_region(as64core.XCAM_REGION)
            lower = np.array(self.lower_bound, dtype="uint8")
            upper = np.array(self.upper_bound, dtype="uint8")

            mask = cv2.inRange(xcam, lower, upper)
            output = cv2.bitwise_and(xcam, xcam, mask=mask)

            if not is_black(output, 0.1, 0.7):
                as64core.split()
                as64core.fps = 10
                as64core.fadeout_count = 0
                as64core.set_intro_ended(True)
                return self.signals["START"]

        return self.signals["LOOP"]

    def on_transition(self):
        as64core.fps = 10
        as64core.enable_predictions(True)

        super().on_transition()
