import time

import cv2
import numpy as np

import as64core

from as64core.resource_utils import resource_path

from as64core import config
from as64core.image_utils import is_black, is_white
from as64core.processing import Process


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
    def __init__(self):
        super().__init__()

        # Register Signals
        self.register_signal("FADEOUT")
        self.register_signal("START")

        self._star_skip_enabled = config.get("general", "mid_run_start_enabled")

        self._prev_prediction = -1
        self._jump_predictions = 0

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["FADEOUT"]
        else:
            if as64core.split_index() > 0:
                prev_split_star = as64core.route.splits[as64core.split_index()-1].star_count
            else:
                prev_split_star = as64core.route.initial_star

            if as64core.prediction_info.prediction == as64core.star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                as64core.enable_fade_count(True)
                as64core.enable_xcam_count(True)
                as64core.set_in_game(True)
                return self.signals["START"]
            elif self._star_skip_enabled and prev_split_star <= as64core.prediction_info.prediction <= as64core.current_split().star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                if as64core.prediction_info.prediction == self._prev_prediction:
                    self._jump_predictions += 1
                else:
                    self._jump_predictions = 0

                if self._jump_predictions >= 4:
                    as64core.enable_fade_count(True)
                    as64core.enable_xcam_count(True)
                    as64core.set_star_count(as64core.prediction_info.prediction)
                    self._jump_predictions = 0
                    self._prev_prediction = -1
                    as64core.set_in_game(True)
                    return self.signals["START"]

                self._prev_prediction = as64core.prediction_info.prediction

        return self.signals["LOOP"]

    def on_transition(self):
        as64core.enable_fade_count(False)
        as64core.fps = 6

        super().on_transition()


class ProcessRunStartUpSegment(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("FADEOUT")
        self.register_signal("START")
        self._star_skip_enabled = config.get("general", "mid_run_start_enabled")
        self._prev_prediction = -1
        self._jump_predictions = 0

    def execute(self):
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["FADEOUT"]
        else:
            if as64core.split_index() > 0:
                prev_split_star = as64core.route.splits[as64core.split_index()-1].star_count
            else:
                prev_split_star = as64core.route.initial_star

            if as64core.prediction_info.prediction == as64core.star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                as64core.enable_fade_count(True)
                as64core.enable_xcam_count(True)
                return self.signals["START"]
            elif self._star_skip_enabled and prev_split_star <= as64core.prediction_info.prediction <= as64core.current_split().star_count and as64core.prediction_info.probability > config.get("thresholds", "probability_threshold"):
                if as64core.prediction_info.prediction == self._prev_prediction:
                    self._jump_predictions += 1
                else:
                    self._jump_predictions = 0

                if self._jump_predictions >= 4:
                    as64core.enable_fade_count(True)
                    as64core.enable_xcam_count(True)
                    as64core.set_star_count(as64core.prediction_info.prediction)
                    self._jump_predictions = 0
                    self._prev_prediction = -1
                    return self.signals["START"]

                self._prev_prediction = as64core.prediction_info.prediction

        return self.signals["LOOP"]

    def on_transition(self):
        as64core.enable_fade_count(False)
        as64core.fps = 6

        super().on_transition()


class ProcessStarCount(Process):
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
        as64core.fps = config.get("advanced", "star_process_frame_rate")
        as64core.enable_predictions(True)
        as64core.enable_xcam_count(True)
        super().on_transition()


class ProcessFadein(Process):
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
        as64core.fps = 29.97
        as64core.enable_predictions(False)
        as64core.fadein()

        super().on_transition()


class ProcessFadeout(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("RESET")
        self.register_signal("COMPLETE")

        self._split_occurred = False

        self._fps = config.get("advanced", "fadeout_process_frame_rate")
        self._reset_threshold = config.get("thresholds", "reset_threshold")
        self._black_threshold = config.get("thresholds", "black_threshold")
        self._undo_threshold = config.get("thresholds", "undo_threshold")

        _, _, reset_width, reset_height = as64core.get_region_rect(as64core.RESET_REGION)
        self._reset_template = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_one"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)
        self._reset_template_2 = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_two"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)

    def execute(self):
        reset_region = as64core.get_region(as64core.RESET_REGION)
        # TODO: SWITCH TO USING FADE_STATUS
        # If centre of screen is black, and the current split conditions are met, trigger split
        if is_black(reset_region, self._black_threshold) and as64core.incoming_split() and as64core.current_split().split_type == as64core.SPLIT_NORMAL:
            as64core.split()
            self._split_occurred = True

        # Check for a match against the reset_template (SM64 logo)
        if self._is_reset(reset_region, self._reset_template):
            as64core.enable_predictions(True)
            self._split_occurred = False
            self._reset()
            return self.signals["RESET"]
        elif self._is_reset(reset_region, self._reset_template_2):
            as64core.enable_predictions(True)
            self._split_occurred = False
            self._reset()
            return self.signals["RESET"]

        # If both star count, and life count are still black, reprocess fadeout, otherwise fadeout completed
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["LOOP"]
        else:
            as64core.enable_predictions(True)
            self._split_occurred = False
            return self.signals["COMPLETE"]

    def _reset(self):
        if not config.get("general", "srl_mode"):
            if as64core.current_time - as64core.last_split < self._undo_threshold:
                as64core.undo()

            as64core.reset()
            # time.sleep(self._restart_split_delay)
            if as64core.start_on_reset:
                as64core.split()

        as64core.enable_fade_count(False)
        as64core.enable_xcam_count(False)
        as64core.set_in_game(False)
        as64core.star_count = as64core.route.initial_star
        #as64core.force_update()

    def _is_reset(self, region, template):
        match = cv2.minMaxLoc(cv2.matchTemplate(region,
                                                template,
                                                cv2.TM_SQDIFF_NORMED))[0]

        if match < config.get("thresholds", "reset_threshold"):
            return True
        else:
            return False

    def on_transition(self):
        as64core.fps = self._fps
        as64core.enable_predictions(False)
        as64core.enable_xcam_count(False)
        super().on_transition()


class ProcessFadeoutNoStar(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("RESET")
        self.register_signal("COMPLETE")

        self._split_occurred = False

        self._fps = config.get("advanced", "fadeout_process_frame_rate")
        self._reset_threshold = config.get("thresholds", "reset_threshold")
        self._black_threshold = config.get("thresholds", "black_threshold")
        self._undo_threshold = config.get("thresholds", "undo_threshold")

        _, _, reset_width, reset_height = as64core.get_region_rect(as64core.RESET_REGION)
        self._reset_template = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_one"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)
        self._reset_template_2 = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_two"))), (reset_width, reset_height), interpolation=cv2.INTER_AREA)

    def execute(self):
        reset_region = as64core.get_region(as64core.RESET_REGION)
        # TODO: SWITCH TO USING FADE_STATUS
        # If centre of screen is black, and the current split conditions are met, trigger split
        if is_black(reset_region, self._black_threshold) and as64core.incoming_split(star_count=False) and as64core.current_split().split_type == as64core.SPLIT_FADE_ONLY:
            as64core.split()
            self._split_occurred = True

        # Check for a match against the reset_template (SM64 logo)
        if as64core.fade_status == self._is_reset(reset_region, self._reset_template):
            as64core.enable_predictions(True)
            self._split_occurred = False
            self._reset()
            return self.signals["RESET"]
        elif self._is_reset(reset_region, self._reset_template_2):
            as64core.enable_predictions(True)
            self._split_occurred = False
            self._reset()
            return self.signals["RESET"]

        # If both star count, and life count are still black, reprocess fadeout, otherwise fadeout completed
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["LOOP"]
        else:
            as64core.enable_predictions(True)
            self._split_occurred = False
            return self.signals["COMPLETE"]

    def _reset(self):
        if not config.get("general", "srl_mode"):
            if as64core.current_time - as64core.last_split < self._undo_threshold:
                as64core.undo()

            as64core.reset()
            if as64core.start_on_reset:
                as64core.split()

        as64core.enable_fade_count(False)
        as64core.enable_xcam_count(False)
        as64core.set_in_game(False)
        as64core.star_count = as64core.route.initial_star

    def _is_reset(self, region, template):
        match = cv2.minMaxLoc(cv2.matchTemplate(region,
                                                template,
                                                cv2.TM_SQDIFF_NORMED))[0]

        if match < config.get("thresholds", "reset_threshold"):
            return True
        else:
            return False

    def on_transition(self):
        as64core.fps = self._fps
        as64core.enable_predictions(False)
        as64core.enable_xcam_count(False)
        super().on_transition()


class ProcessFadeoutResetOnly(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("RESET")
        self.register_signal("COMPLETE")

        self._fps = config.get("advanced", "fadeout_process_frame_rate")
        self._reset_threshold = config.get("thresholds", "reset_threshold")
        self._black_threshold = config.get("thresholds", "black_threshold")
        self._undo_threshold = config.get("thresholds", "undo_threshold")

        _, _, reset_width, reset_height = as64core.get_region_rect(as64core.RESET_REGION)
        self._reset_template = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_one"))),
                                          (reset_width, reset_height), interpolation=cv2.INTER_AREA)
        self._reset_template_2 = cv2.resize(cv2.imread(resource_path(config.get("advanced", "reset_frame_two"))),
                                            (reset_width, reset_height), interpolation=cv2.INTER_AREA)

    def execute(self):
        reset_region = as64core.get_region(as64core.RESET_REGION)

        # Check for a match against the reset_template (SM64 logo)
        if self._is_reset(reset_region, self._reset_template):
            as64core.enable_predictions(True)
            self._reset()
            return self.signals["RESET"]
        elif self._is_reset(reset_region, self._reset_template_2):
            as64core.enable_predictions(True)
            self._reset()
            return self.signals["RESET"]

        # If both star count, and life count are still black, reprocess fadeout, otherwise fadeout completed
        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["LOOP"]
        else:
            as64core.enable_predictions(True)
            return self.signals["COMPLETE"]

    def _reset(self):
        if not config.get("general", "srl_mode"):
            if as64core.current_time - as64core.last_split < self._undo_threshold:
                as64core.undo()

            as64core.reset()
            if as64core.start_on_reset:
                as64core.split()

        as64core.enable_fade_count(False)
        as64core.enable_xcam_count(False)
        as64core.set_in_game(False)
        as64core.star_count = as64core.route.initial_star
        #as64core.force_update()

    def _is_reset(self, region, template):
        match = cv2.minMaxLoc(cv2.matchTemplate(region,
                                                template,
                                                cv2.TM_SQDIFF_NORMED))[0]

        if match < config.get("thresholds", "reset_threshold"):
            return True
        else:
            return False

    def on_transition(self):
        as64core.fps = self._fps
        as64core.enable_predictions(False)
        as64core.enable_xcam_count(False)
        super().on_transition()


class ProcessPostFadeout(Process):
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

        if as64core.incoming_split():
            if as64core.xcam_count == 0 and as64core.in_xcam:
                as64core.split()
            elif as64core.xcam_count == as64core.current_split().on_xcam:
                as64core.xcam_count = 0
                as64core.split()

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
        self._power_found = False
        as64core.enable_predictions(True)
        as64core.enable_xcam_count(True)
        as64core.fps = 15

        super().on_transition()


class ProcessFlashCheck(Process):
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
        as64core.fps = 29.97
        as64core.enable_predictions(True)
        self._running_total = 0
        self._flash_count = 0
        self._prev_prediction = 0

        super().on_transition()


class ProcessReset(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("RESET")

    def execute(self):
        return self.signals["RESET"]

    def on_transition(self):
        super().on_transition()


class ProcessResetNoStart(Process):
    def __init__(self,):
        super().__init__()
        self.register_signal("RESET")
        self._restart_split_delay = config.get("advanced", "restart_split_delay")

    def execute(self):
        # if not config.get("general", "srl_mode"):
        #     if as64core.current_time - as64core.last_split < 4:
        #         as64core.undo()
        #
        #     as64core.reset()
        #
        # as64core.enable_fade_count(False)
        # as64core.enable_xcam_count(False)
        # as64core.set_in_game(False)
        # as64core.star_count = as64core.route.initial_star
        # as64core.force_update()

        return self.signals["RESET"]

    def on_transition(self):
        super().on_transition()


class ProcessDummy(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("COMPLETE")

    def execute(self):
        return self.signals["COMPLETE"]

    def on_transition(self):
        super().on_transition()


class ProcessFileSelectSplit(Process):
    def __init__(self):
        super().__init__()
        self.register_signal("FADEOUT")
        self.register_signal("COMPLETE")

        self._star_skip_enabled = config.get("general", "mid_run_start_enabled")
        self._prev_prediction = -1
        self._jump_predictions = 0

        self._restart_split_delay = 1.2012 + (config.get("advanced", "file_select_frame_offset") / 29.97)

    def execute(self):
        region = as64core.get_region(as64core.FADEOUT_REGION)

        if as64core.fade_status in (as64core.FADEOUT_COMPLETE, as64core.FADEOUT_PARTIAL):
            return self.signals["FADEOUT"]
        else:
            if as64core.split_index() > 0:
                prev_split_star = as64core.route.splits[as64core.split_index() - 1].star_count
            else:
                prev_split_star = as64core.route.initial_star

            if as64core.prediction_info.prediction == as64core.star_count and as64core.prediction_info.probability > config.get(
                    "thresholds", "probability_threshold"):
                as64core.enable_fade_count(True)
                as64core.enable_xcam_count(True)
                as64core.set_in_game(True)
                return self.signals["COMPLETE"]
            elif self._star_skip_enabled and prev_split_star <= as64core.prediction_info.prediction <= as64core.current_split().star_count and as64core.prediction_info.probability > config.get(
                    "thresholds", "probability_threshold"):
                if as64core.prediction_info.prediction == self._prev_prediction:
                    self._jump_predictions += 1
                else:
                    self._jump_predictions = 0

                if self._jump_predictions >= 4:
                    as64core.enable_fade_count(True)
                    as64core.enable_xcam_count(True)
                    as64core.set_star_count(as64core.prediction_info.prediction)
                    self._jump_predictions = 0
                    self._prev_prediction = -1
                    as64core.set_in_game(True)
                    return self.signals["COMPLETE"]

                self._prev_prediction = as64core.prediction_info.prediction

        if as64core.fadein_count == 2:
            region_int = region.astype(int)
            region_int_b, region_int_g, region_int_r = region_int.transpose(2, 0, 1)
            mask = (np.abs(region_int_r - region_int_g) > 25)

            region[mask] = [0, 0, 0]

            if np.any(region == [0, 0, 0]):
                try:
                    time.sleep(self._restart_split_delay)
                except ValueError:
                    pass
                as64core.fadein_count = 0
                as64core.fadeout_count = 0
                as64core.split()
                as64core.set_in_game(True)
                return self.signals["COMPLETE"]

        return self.signals["LOOP"]

    def on_transition(self):
        super().on_transition()
        as64core.fps = 29.97
        as64core.enable_fade_count(True)
