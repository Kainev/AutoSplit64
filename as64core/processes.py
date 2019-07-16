import time

import cv2
import numpy as np

import as64core

from as64core.resource_utils import resource_path

from as64core import config
from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessRunStart(Process):
    FADEOUT = Signal("PRS_FADEOUT")
    START = Signal("PRS_START")

    def __init__(self):
        super().__init__()
        self._star_skip_enabled = config.get("general", "mid_run_start_enabled")
        self._prev_prediction = -1
        self._jump_predictions = 0

    def execute(self):
        print(as64core.prediction_info.prediction, as64core.prediction_info.probability)
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return ProcessRunStart.FADEOUT
        else:
            if as64core.split_index() > 0:
                prev_split_star = as64core.route.splits[as64core.split_index()-1].star_count
            else:
                prev_split_star = as64core.route.initial_star

            if as64core.prediction_info.prediction == as64core.star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                as64core.enable_fade_count(True)
                return ProcessRunStart.START
            elif self._star_skip_enabled and prev_split_star <= as64core.prediction_info.prediction <= as64core.current_split().star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                if as64core.prediction_info.prediction == self._prev_prediction:
                    self._jump_predictions += 1
                else:
                    self._jump_predictions = 0

                if self._jump_predictions >= 4:
                    as64core.enable_fade_count(True)
                    as64core.set_star_count(as64core.prediction_info.prediction)
                    self._jump_predictions = 0
                    self._prev_prediction = -1
                    return ProcessRunStart.START

                self._prev_prediction = as64core.prediction_info.prediction

        return Process.LOOP

    def on_transition(self):
        print("PROCESS RUN START")
        as64core.enable_fade_count(False)
        as64core.fps = 6

        super().on_transition()


class ProcessStarCount(Process):
    FADEOUT = Signal("PSC_FADEOUT")
    FADEIN = Signal("PSC_FADEIN")

    def __init__(self):
        super().__init__()

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessStarCount.FADEOUT

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return ProcessStarCount.FADEIN

        return Process.LOOP

    def on_transition(self):
        print("PROCESS STAR COUNT")
        as64core.fps = config.get("advanced", "star_process_frame_rate")
        as64core.enable_predictions(True)

        super().on_transition()


class ProcessFadein(Process):
    COMPLETE = Signal("PFI_COMPLETE")

    def __init__(self):
        super().__init__()

    def execute(self):
        if as64core.incoming_split() and as64core.fade_status == as64core.FADEIN_COMPLETE:
            as64core.split()

        if as64core.fade_status == as64core.FADEIN_PARTIAL:
            return Process.LOOP
        else:
            return ProcessFadein.COMPLETE

    def on_transition(self):
        print("PROCESS FADEIN")
        as64core.fps = 29.97
        as64core.enable_predictions(False)
        as64core.fadein()

        super().on_transition()


class ProcessFadeout(Process):
    RESET = Signal("PFO_RESET")
    COMPLETE = Signal("PFO_COMPLETE")

    def __init__(self):
        super().__init__()

        self._split_occurred = False

        self._fps = config.get("advanced", "fadeout_process_frame_rate")
        self._reset_threshold = config.get("thresholds", "reset_threshold")
        self._black_threshold = config.get("thresholds", "black_threshold")

        _, _, reset_width, reset_height = as64core.get_region_rect(as64core.RESET_REGION)
        self._reset_template = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_one"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)
        self._reset_template_2 = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_two"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)

    def execute(self):
        reset_region = as64core.get_region(as64core.RESET_REGION)

        # TODO: SWITCH TO USING FADE_STATUS
        # If centre of screen is black, and the current split conditions are met, trigger split
        if is_black(reset_region, self._black_threshold) and as64core.incoming_split():
            as64core.split()
            self._split_occurred = True

        # Check for a match against the reset_template (SM64 logo)
        match = cv2.minMaxLoc(cv2.matchTemplate(reset_region,
                                                self._reset_template,
                                                cv2.TM_SQDIFF_NORMED))[0]

        if match < self._reset_threshold:
            # If this fadeout triggered a split, undo before reset
            if self._split_occurred:
                as64core.undo()
            as64core.enable_predictions(True)
            return ProcessFadeout.RESET
        else:
            match2 = cv2.minMaxLoc(cv2.matchTemplate(reset_region,
                                                     self._reset_template_2,
                                                     cv2.TM_SQDIFF_NORMED))[0]

            if match2 < config.get("thresholds", "reset_threshold"):
                # If this fadeout triggered a split, undo before reset
                if self._split_occurred:
                    as64core.undo()
                as64core.enable_predictions(True)
                return ProcessFadeout.RESET

        # If both star count, and life count are still black, reprocess fadeout, otherwise fadeout completed
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return Process.LOOP
        else:
            as64core.enable_predictions(True)
            return ProcessFadeout.COMPLETE

    def on_transition(self):
        print("PROCESS FADEOUT")
        as64core.fps = self._fps
        self._split_occurred = False
        as64core.enable_predictions(False)
        super().on_transition()


class ProcessPostFadeout(Process):
    FADEOUT = Signal("PPF_FADEOUT")
    FADEIN = Signal("PPF_FADEIN")
    FLASH = Signal("PPF_FLASH")
    COMPLETE = Signal("PPF_COMPLETE")

    def __init__(self):
        super().__init__()

        self.power_lower_bound = [215, 40, 0]
        self.power_upper_bound = [255, 150, 0]
        self._power_found = False

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessPostFadeout.FADEOUT

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return ProcessPostFadeout.FADEIN

        if as64core.prediction_info.prediction in (121, 122) and self.loop_time() > 1:
            return ProcessPostFadeout.FLASH

        if time.time() - as64core.collection_time > 11:
            self._death_check()

        if self.loop_time() < 6:
            return Process.LOOP
        else:
            return ProcessPostFadeout.COMPLETE

    def _death_check(self):
        if 2 < self.loop_time() < 3:
            self._power_found = self._power_check()
        elif self.loop_time() >= 3 and self._power_found:
            self._power_found = self._power_check()
            if not self._power_found:
                as64core.fadeout_count = max(as64core.fadeout_count - 2, 0)

    def _power_check(self):
        power_region = as64core.get_region(as64core.POWER_REGION)

        lower = np.array(self.power_lower_bound, dtype="uint8")
        upper = np.array(self.power_upper_bound, dtype="uint8")

        power_mask = cv2.inRange(power_region, lower, upper)
        output = cv2.bitwise_and(power_region, power_region, mask=power_mask)

        return not is_black(output, 0.1, 0.9)

    def on_transition(self):
        print("PROCESS POST FADEOUT")

        self._power_found = False
        as64core.enable_predictions(True)
        as64core.fps = 15

        super().on_transition()


class ProcessFlashCheck(Process):
    FADEOUT = Signal("PPF_FADEOUT")
    FADEIN = Signal("PPF_FADEIN")
    COMPLETE = Signal("PFC_COMPLETE")

    def __init__(self):
        super().__init__()

        self._running_total = 0
        self._prev_prediction = 0
        self._flash_count = 0

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessFlashCheck.FADEOUT

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return ProcessFlashCheck.FADEIN

        if as64core.prediction_info.prediction in (121, 122):
            normalized_prediction = 1
        else:
            normalized_prediction = -1

        if normalized_prediction == self._prev_prediction * -1:
            self._flash_count += 1

        self._running_total += normalized_prediction
        self._prev_prediction = normalized_prediction

        if -10 < self._running_total < 10 and self._flash_count >= 4:
            print("Flash Detected!")
            print("Running Total:", self._running_total, "Flash Count:", self._flash_count)
            if time.time() - as64core.collection_time > 15:
                print("Increment Star from Flash!")
                as64core.set_star_count(as64core.star_count + 1)

                if as64core.current_split().star_count == as64core.star_count:

                    if as64core.current_split().on_fadeout == 1:
                        as64core.skip()
                    else:
                        as64core.fadeout_count += 1

            return ProcessFlashCheck.COMPLETE

        if self.loop_time() < 2:
            return Process.LOOP
        else:
            return ProcessFlashCheck.COMPLETE

    def on_transition(self):
        print("PROCESS FLASH CHECK")

        as64core.fps = 29.97
        as64core.enable_predictions(True)
        self._running_total = 0
        self._flash_count = 0
        self._prev_prediction = 0

        super().on_transition()


class ProcessReset(Process):
    RESET = Signal("PR_RESET")

    def __init__(self,):
        super().__init__()
        self._restart_split_delay = config.get("advanced", "restart_split_delay")

    def execute(self):
        if not config.get("general", "srl_mode"):
            as64core.reset()
            time.sleep(self._restart_split_delay)
            as64core.split()

        as64core.enable_fade_count(False)
        as64core.star_count = as64core.route.initial_star
        as64core.force_update()

        return ProcessReset.RESET

    def on_transition(self):
        print("PROCESS RESET")

        super().on_transition()


class ProcessFinalStageEntry(Process):
    ENTERED = Signal("PFSE_ENTERED")
    FADEOUT = Signal("PFSE_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.bowser_lower_bound = config.get("split_final_star", "stage_lower_bound")
        self.bowser_upper_bound = config.get("split_final_star", "stage_upper_bound")

    def execute(self):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessFinalStageEntry.FADEOUT

        lower = np.array(self.bowser_lower_bound, dtype="uint8")
        upper = np.array(self.bowser_upper_bound, dtype="uint8")

        star_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=star_mask)

        if not is_black(output, 0.1, 0.9):
            return ProcessFinalStageEntry.ENTERED
        else:
            return Process.LOOP

    def on_transition(self):
        print("PROCESS FINAL STAGE ENTRY")

        as64core.fps = 10

        super().on_transition()


class ProcessFinalStarSpawn(Process):
    SPAWNED = Signal("PFSS_SPAWNED")
    FADEOUT = Signal("PFSS_FADEOUT")

    def __init__(self):
        super().__init__()
        self._iteration_value = {0: 1, 1: 4, 2: 1}
        self._looping_iteration = 0

        self.star_lower_bound = config.get("split_final_star", "star_lower_bound")
        self.star_upper_bound = config.get("split_final_star", "star_upper_bound")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessFinalStarSpawn.FADEOUT

        if self._star_visible() and self.loop_time() > 30:
            if self._looping_iteration == len(self._iteration_value):
                print("spawned :)")
                return ProcessFinalStarSpawn.SPAWNED
            else:
                try:
                    print("iter", self._looping_iteration)
                    time.sleep(self._iteration_value[self._looping_iteration])
                except IndexError:
                    pass

            self._looping_iteration += 1

            return Process.LOOP
        else:
            self._looping_iteration = 0

        return Process.LOOP

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
    COMPLETE = Signal("PFSG_COMPLETE")
    FADEOUT = Signal("PFSG_FADEOUT")

    def __init__(self):
        super().__init__()

        self.star_lower_bound = config.get("split_final_star", "star_lower_bound")
        self.star_upper_bound = config.get("split_final_star", "star_upper_bound")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessFinalStageEntry.FADEOUT

        if not self._star_visible():
            print("Grabbed!")
            as64core.split()
            return ProcessFinalStarGrab.COMPLETE

        return Process.LOOP

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


class ProcessFindDDDPortal(Process):
    FOUND = Signal("PFDP_FOUND")
    FADEOUT = Signal("PFDP_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.portal_lower_bound = config.get("split_ddd_enter", "portal_lower_bound")
        self.portal_upper_bound = config.get("split_ddd_enter", "portal_upper_bound")

    def execute(self):
        no_hud = as64core.get_region(as64core.GAME_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessFindDDDPortal.FADEOUT

        lower = np.array(self.portal_lower_bound, dtype="uint8")
        upper = np.array(self.portal_upper_bound, dtype="uint8")

        portal_mask = cv2.inRange(no_hud, lower, upper)
        output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)

        if not is_black(output, 0.1, 0.99):
            return ProcessFindDDDPortal.FOUND
        else:
            return Process.LOOP

    def on_transition(self):
        print("PROCESS FIND DDD PORTAL")
        as64core.fps = 10

        super().on_transition()


class ProcessDDDEntry(Process):
    ENTERED = Signal("PDE_ENTERED")
    FADEOUT = Signal("PDE_FADEOUT")

    def __init__(self,):
        super().__init__()

        self.lower_bound = np.array(config.get("split_ddd_enter", "hat_lower_bound"), dtype="uint8")
        self.upper_bound = np.array(config.get("split_ddd_enter", "hat_upper_bound"), dtype="uint8")

    def execute(self):
        no_hud = as64core.get_region(as64core.NO_HUD_REGION)

        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessDDDEntry.FADEOUT

        if not cv2.inRange(no_hud, self.lower_bound, self.upper_bound).any():
            as64core.split()
            return ProcessDDDEntry.ENTERED
        else:
            return Process.LOOP

    def on_transition(self):
        #
        print("PROCESS DDD ENTRY")
        as64core.fps = 10

        super().on_transition()


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
            print("GREEN FOUND!")
            portal_mask = cv2.inRange(no_hud, self.green_lower_bound, self.green_upper_bound)
            output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)
            cv2.imwrite("green.png", output)
            self.green_found = True

        if cv2.inRange(no_hud, self.purple_lower_bound, self.purple_upper_bound).any() and cv2.inRange(no_hud, self.green_lobby_lower_bound, self.green_lobby_upper_bound).any() and not self.green_found:
            print("HELLO!")
            #portal_mask = cv2.inRange(no_hud, self.purple_lower_bound, self.purple_upper_bound)
            #output = cv2.bitwise_and(no_hud, no_hud, mask=portal_mask)
            #cv2.imwrite("purple.png", output)
            self.orange_found = True

        return Process.LOOP

    def on_transition(self):
        print("PROCESS LBLJ")

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


class ProcessIdle(Process):
    FADEOUT = Signal("PDE_FADEOUT")

    def __init__(self,):
        super().__init__()

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return ProcessIdle.FADEOUT

        return Process.LOOP

    def on_transition(self):
        as64core.enable_predictions(False)
        as64core.fps = 10
        super().on_transition()
