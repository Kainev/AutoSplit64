import time

import cv2
import numpy as np

import as64core

from as64core.resource_utils import resource_path

from as64core import config
from as64core.image_utils import is_black
from as64core.processing import Process, Signal


class ProcessWait(Process):

    def __init__(self,):
        super().__init__()

        self.register_signal("FADEOUT")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        return self.signals["LOOP"]

    def on_transition(self):
        as64core.enable_predictions(False)
        as64core.fps = 10
        super().on_transition()


class ProcessRunStart(Process):
    FADEOUT = Signal("PRS_FADEOUT")
    START = Signal("PRS_START")

    def __init__(self):
        super().__init__()
        self.register_signal("FADEOUT")
        self.register_signal("START")
        self._star_skip_enabled = config.get("general", "mid_run_start_enabled")
        self._prev_prediction = -1
        self._jump_predictions = 0

    def execute(self):
        print(as64core.prediction_info.prediction, as64core.prediction_info.probability)
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["FADEOUT"]
        else:
            if as64core.split_index() > 0:
                prev_split_star = as64core.route.splits[as64core.split_index()-1].star_count
            else:
                prev_split_star = as64core.route.initial_star

            if as64core.prediction_info.prediction == as64core.star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                as64core.enable_fade_count(True)
                return self.signals["START"]
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
                    return self.signals["START"]

                self._prev_prediction = as64core.prediction_info.prediction

        return self.signals["LOOP"]

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
        self.register_signal("FADEOUT")
        self.register_signal("FADEIN")

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return self.signals["FADEIN"]

        return self.signals["LOOP"]

    def on_transition(self):
        print("PROCESS STAR COUNT")
        as64core.fps = config.get("advanced", "star_process_frame_rate")
        as64core.enable_predictions(True)

        super().on_transition()


class ProcessFadein(Process):
    COMPLETE = Signal("PFI_COMPLETE")

    def __init__(self):
        super().__init__()
        self.register_signal("COMPLETE")

    def execute(self):
        if as64core.incoming_split() and as64core.fade_status == as64core.FADEIN_COMPLETE:
            as64core.split()

        if as64core.fade_status == as64core.FADEIN_PARTIAL:
            return self.signals["LOOP"]
        else:
            # TODO: BUG: Fadein transition oscillation
            # Returns complete signal, transitions to star_count, is still white, transitions back on loop
            return self.signals["COMPLETE"]

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
        self.register_signal("RESET")
        self.register_signal("COMPLETE")

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
            return self.signals["RESET"]
        else:
            match2 = cv2.minMaxLoc(cv2.matchTemplate(reset_region,
                                                     self._reset_template_2,
                                                     cv2.TM_SQDIFF_NORMED))[0]

            if match2 < config.get("thresholds", "reset_threshold"):
                # If this fadeout triggered a split, undo before reset
                if self._split_occurred:
                    as64core.undo()
                as64core.enable_predictions(True)
                return self.signals["RESET"]

        # If both star count, and life count are still black, reprocess fadeout, otherwise fadeout completed
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["LOOP"]
        else:
            as64core.enable_predictions(True)
            return self.signals["COMPLETE"]

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
        self.register_signal("FADEOUT")
        self.register_signal("FADEIN")
        self.register_signal("FLASH")
        self.register_signal("COMPLETE")

        self.power_lower_bound = [215, 40, 0]
        self.power_upper_bound = [255, 150, 0]
        self._power_found = False

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return self.signals["FADEIN"]

        if as64core.prediction_info.prediction in (121, 122) and self.loop_time() > 1:
            return self.signals["FLASH"]

        if time.time() - as64core.collection_time > 11:
            self._death_check()

        if self.loop_time() < 6:
            return self.signals["LOOP"]
        else:
            return self.signals["COMPLETE"]

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
        self.register_signal("FADEOUT")
        self.register_signal("FADEIN")
        self.register_signal("COMPLETE")

        self._running_total = 0
        self._prev_prediction = 0
        self._flash_count = 0

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_PARTIAL, as64core.FADEOUT_COMPLETE):
            return self.signals["FADEOUT"]

        if as64core.fade_status in (as64core.FADEIN_PARTIAL, as64core.FADEIN_COMPLETE):
            return self.signals["FADEIN"]

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

            return self.signals["COMPLETE"]

        if self.loop_time() < 2:
            return self.signals["LOOP"]
        else:
            return self.signals["COMPLETE"]

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
        self.register_signal("RESET")
        self._restart_split_delay = config.get("advanced", "restart_split_delay")

    def execute(self):
        if not config.get("general", "srl_mode"):
            as64core.reset()
            time.sleep(self._restart_split_delay)
            as64core.split()

        as64core.enable_fade_count(False)
        as64core.star_count = as64core.route.initial_star
        as64core.force_update()

        return self.signals["RESET"]

    def on_transition(self):
        print("PROCESS RESET")

        super().on_transition()
