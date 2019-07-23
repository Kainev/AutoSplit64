import cv2
import numpy as np

import as64core

from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessXCam(Process):
    FOUND = Signal("PFDP_FOUND")
    FADEOUT = Signal("PFDP_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.lower_bound = [0, 0, 60]
        self.upper_bound = [17, 23, 161]

    def execute(self):
        xcam = as64core.get_region(as64core.XCAM_REGION)

        lower = np.array(self.lower_bound, dtype="uint8")
        upper = np.array(self.upper_bound, dtype="uint8")

        mask = cv2.inRange(xcam, lower, upper)
        output = cv2.bitwise_and(xcam, xcam, mask=mask)

        if not is_black(output, 0.1, 0.99):
            print("XCAM FOUND")
        else:
            return Process.LOOP

    def on_transition(self):
        print("PROCESS XCAM")
        as64core.fps = 10

        super().on_transition()
