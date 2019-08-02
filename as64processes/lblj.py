import time

import cv2
import numpy as np

import as64core

from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessLBLJ2(Process):
    FOUND = Signal("PLBLJ_FOUND")
    FADEOUT = Signal("PLBLJ_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.green_lower_bound = np.array([0, 86, 0], dtype="uint8")
        self.green_upper_bound = np.array([10, 100, 20], dtype="uint8")

        self.purple_lower_bound = np.array([170, 0, 130], dtype="uint8")
        self.purple_upper_bound = np.array([255, 45, 210], dtype="uint8")

        self.green_lobby_lower_bound = np.array([40, 0, 0], dtype="uint8")
        self.green_lobby_upper_bound = np.array([60, 8, 8], dtype="uint8")

        self.orange_found = False
        self.green_found = False

    def execute(self):
        no_hud = as64core.get_region(as64core.GAME_REGION)

        if as64core.fade_status == as64core.FADEOUT_COMPLETE:
            if self.orange_found and self.green_found:
                as64core.split()
            return ProcessLBLJ.FADEOUT

        if cv2.inRange(no_hud, self.green_lower_bound, self.green_upper_bound).any():
            portal_mask = cv2.inRange(no_hud, self.green_lower_bound, self.green_upper_bound)
            output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)
            cv2.imwrite("green.png", output)
            self.green_found = True

        if cv2.inRange(no_hud, self.purple_lower_bound, self.purple_upper_bound).any() and cv2.inRange(no_hud, self.green_lobby_lower_bound, self.green_lobby_upper_bound).any() and not self.green_found:
            #portal_mask = cv2.inRange(no_hud, self.purple_lower_bound, self.purple_upper_bound)
            #output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)
            #cv2.imwrite("purple.png", output)
            self.orange_found = True

        return Process.LOOP

    def on_transition(self):
        self.orange_found = False
        self.green_found = False

        as64core.fps = 14
        super().on_transition()


class ProcessLBLJ(Process):
    FOUND = Signal("PLBLJ_FOUND")
    FADEOUT = Signal("PLBLJ_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.green_lower_bound = np.array([0, 86, 0], dtype="uint8")
        self.green_upper_bound = np.array([10, 120, 60], dtype="uint8")

        self.red_lower_bound = np.array([0, 0, 90], dtype="uint8")
        self.red_upper_bound = np.array([30, 30, 150], dtype="uint8")

        self.grey_lower_bound = np.array([70, 50, 50], dtype="uint8")
        self.grey_upper_bound = np.array([150, 130, 130], dtype="uint8")

        self.green_found_time = 0
        self.red_found_time = 0
        self.grey_found_time = 0

    def execute(self):
        no_hud = as64core.get_region(as64core.GAME_REGION)

        if as64core.fade_status == as64core.FADEOUT_COMPLETE:
            c_time = time.time()
            print("Green", c_time - self.green_found_time)
            print("Red", c_time - self.red_found_time)
            print("Grey", c_time - self.grey_found_time)

            if c_time - self.red_found_time < 0.4 and c_time - self.green_found_time < 0.4 and c_time - self.grey_found_time > 0.75:
                as64core.split()
            return ProcessLBLJ.FADEOUT

        red_mask = cv2.inRange(no_hud, self.red_lower_bound, self.red_upper_bound)
        red_output = cv2.bitwise_and(no_hud, no_hud, mask=red_mask)

        if not is_black(red_output, 0.1, 0.99):
            print("RED")
            self.red_found_time = time.time()

        grey_mask = cv2.inRange(no_hud, self.grey_lower_bound, self.grey_upper_bound)
        grey_output = cv2.bitwise_and(no_hud, no_hud, mask=grey_mask)

        if not is_black(grey_output, 0.16, 0.88):
            cv2.imwrite("grey.png", grey_output)
            print("GREY!")
            self.grey_found_time = time.time()


        if cv2.inRange(no_hud, self.green_lower_bound, self.green_upper_bound).any():
            print("GREEN FOUND!")
            self.green_found_time = time.time()

        return Process.LOOP

    def on_transition(self):
        print("PROCESS LBLJ")

        self.green_found_time = 0
        self.red_found_time = 0
        self.grey_found_time = 0

        as64core.fps = 24
        super().on_transition()
