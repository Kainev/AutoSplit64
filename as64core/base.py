import time
from threading import Thread
import logging

import cv2
import numpy as np

from . import config, livesplit
from .game_capture import GameCapture
from .model import Model, PredictionInfo
from .image_utils import is_black, is_white, convert_to_cv2
from .route_loader import load as load_route
from .processing import ProcessorSwitch

from .constants import (
    NO_FADE,
    FADEOUT_PARTIAL,
    FADEOUT_COMPLETE,
    FADEIN_PARTIAL,
    FADEIN_COMPLETE,
    STAR_REGION,
    LIFE_REGION,
    FADEOUT_REGION,
    RESET_REGION,
    FADEIN_REGION,
    XCAM_REGION,
    SPLIT_INITIAL
)


class Base(Thread):
    # TODO: Add all error messages to constants with associated error code
    def __init__(self, module):
        super().__init__()

        global as64
        as64 = module

        # Load config
        config.load_config()

        # Connect to LiveSplit
        self._ls_socket = livesplit.init_socket()
        livesplit.connect(self._ls_socket)

        # Initialize Game Capture
        if config.get("game", "override_version"):
            version = config.get("game", "version")
        else:
            try:
                version = self._route.version
            except AttributeError:
                # TODO: What is this doing? Why are we ever passing the path into the version?
                version = config.get("route", "path")

        # Initialize the Game Capture
        self._game_capture = GameCapture(config.get("game", "process_name"), config.get("game", "game_region"), version)

        # Initialise Prediction Model
        self._model = Model(config.get("model", "path"), config.get("model", "width"), config.get("model", "height"))

        # Main Loop Toggle
        self._running = False

        # Operation Mode
        self._operation_mode = as64.CONFIRMATION_MODE

        # Splitter Functionality Flags
        self._count_fades = False
        self._count_xcams = False
        self._make_predictions = True

        # Fadeout
        self._fade_start_time = 0
        self._minimum_fadeout_time = 0.4

        # X-Cam Detection
        self._xcam_found_time = 0
        self._split_on_current_xcam = False
        self._xcam_point_x_ratio = 5/23
        self._xcam_point_y_ratio = 16/23
        _, _, self._xcam_region_width, self._xcam_region_height = self._game_capture.get_region_rect(XCAM_REGION)

        # Initialize ProcessorSwitch
        self._processor_switch = ProcessorSwitch()

        # Star Skip Error Correction
        self._matching_consecutive_predictions = 0
        self._minimum_consecutive_predictions = config.get("error", "minimum_consecutive_prediction")
        self._previous_prediction = as64.prediction_info
        self._max_star_skip = config.get("error", "max_star_skip")
        self._star_skip_enabled = config.get("error", "star_skip")

        #
        self._intro_ended = False

        # Load Route
        self._route = load_route(config.get("route", "path"))

        try:
            self._route_length = len(self._route.splits)
            self._current_split = self._route.splits[0]
        except AttributeError:
            self._route_length = 0
            self._current_split = None

        # Callback Listeners
        self._update_listener = None
        self._error_listener = None

        # Load configuration
        self._black_threshold = config.get("thresholds", "black_threshold")
        self._white_threshold = config.get("thresholds", "white_threshold")
        self._xcam_lower_bound = np.array(config.get("split_xcam", "lower_bound"), dtype="uint8")
        self._xcam_upper_bound = np.array(config.get("split_xcam", "upper_bound"), dtype="uint8")
        self._xcam_threshold = config.get("thresholds", "xcam_pixel_threshold")
        self._xcam_bg_threshold = config.get("thresholds", "xcam_bg_threshold")
        self._xcam_bg_activation = config.get("thresholds", "xcam_bg_activation")
        self._xcam_rg_threshold = config.get("thresholds", "xcam_rg_threshold")
        self._xcam_rg_activation = config.get("thresholds", "xcam_rg_activation")
        self._split_cooldown = config.get("general", "split_cooldown")
        self._probability_threshold = config.get("thresholds", "probability_threshold")
        self._confirmation_threshold = config.get("thresholds", "confirmation_threshold")
        self._prediction_processing_length = config.get("error", "processing_length")
        self._undo_prediction_threshold = config.get("error", "undo_threshold")
        self._minimum_undo_count = config.get("error", "minimum_undo_count")
        self._detailed_output = config.get("advanced", "detailed_console_output")

        # Star Analysis Function
        if config.get("general", "operation_mode") == as64.CONFIRMATION_MODE:
            self.analyze_star_count = self._analyze_star_count_confirmation_mode
        else:
            self.analyze_star_count = self._analyze_star_count_probability_mode

        #
        self._predictions = [PredictionInfo(0, 0)] * self._prediction_processing_length

        # Export Variables
        as64._base = self
        as64.route = self._route

        try:
            as64.route_length = self._route_length
            as64.star_count = self._route.initial_star
        except AttributeError:
            pass

        # Export Functions
        as64.start = self.start
        as64.stop = self.stop
        as64.set_star_count = self.set_star_count
        as64.enable_predictions = self.enable_predictions
        as64.enable_fade_count = self.enable_fade_count
        as64.enable_xcam_count = self.enable_xcam_count
        as64.set_intro_ended = self.set_intro_ended
        as64.get_region = self.get_region
        as64.get_region_rect = self.get_region_rect
        as64.register_split_processor = self.register_split_processor
        as64.set_update_listener = self.set_update_listener
        as64.set_error_listener = self.set_error_listener
        as64.force_update = self._update_occurred
        as64.split = self.split
        as64.reset = self.reset
        as64.skip = self.skip
        as64.undo = self.undo
        as64.incoming_split = self.incoming_split
        as64.current_split = self.current_split
        as64.split_index = self.split_index

        self.logger = logging.getLogger(".log")

    def validity_check(self):
        if not self._game_capture.is_valid():
            self._error_occurred("Could not find " + config.get("game", "process_name"))
            return False

        try:
            self._game_capture.capture()
        except:
            self._error_occurred("Could not capture " + config.get("game", "process_name"))
            return False

        current_capture_size = self._game_capture.get_capture_size()

        if current_capture_size[0] != config.get("game", "capture_size")[0] or current_capture_size[1] != config.get("game", "capture_size")[1]:
            self._error_occurred("Capture windows dimensions have changed since last configuring coordinates. Please reconfigure capture coordinates and generate reset templates.")
            return False

        if not livesplit.check_connection(self._ls_socket):
            self._error_occurred("Could not connect to LiveSplit. Ensure the LiveSplit Server is started.")
            return False

        if not self._route:
            self._error_occurred("Unable to load route " + config.get("route", "path"))
            return False

        if not self._model.valid():
            self._error_occurred("Unable to load prediction model " + config.get("model", "path"))
            return False

        return True

    def stop(self):
        self._running = False

        livesplit.disconnect(self._ls_socket)

    def run(self):
        try:
            self._running = True

            valid = self.validity_check()

            if not valid:
                self.stop()

            self._processor_switch._current_processor = self._current_split.split_type

            while self._running:
                as64.current_time = time.time()

                try:
                    self._game_capture.capture()
                except:
                    self._error_occurred("Unable to capture " + config.get("game", "process_name"))

                ls_index = max(livesplit.split_index(self._ls_socket), 0)
                if ls_index != self.split_index():
                    self.set_split_index(ls_index)

                self.analyze_fade_status()

                if self._make_predictions:
                    self.analyze_star_count()

                if self._count_xcams:
                    self.analyze_xcam_status()

                try:
                    if self._intro_ended:
                        self._processor_switch.execute(self._current_split.split_type)
                    else:
                        self._processor_switch.execute(SPLIT_INITIAL)
                except ConnectionAbortedError:
                    self._error_occurred("LiveSplit connection failed")

                try:
                    as64.execution_time = time.time() - as64.current_time
                    time.sleep(1 / as64.fps - as64.execution_time)
                except ValueError:
                    pass
        except Exception:
            self.logger.error("Fatal Error", exc_info=True)

    def analyze_xcam_status(self):
        xcam = self._game_capture.get_region(XCAM_REGION)

        # Initial threshold mask
        mask = cv2.inRange(xcam, self._xcam_lower_bound, self._xcam_upper_bound)
        output = cv2.bitwise_and(xcam, xcam, mask=mask)

        # Axis relationship mask
        xcam_int = xcam.astype(int)
        xcam_int_b, xcam_int_g, xcam_int_r = xcam_int.transpose(2, 0, 1)
        mask = ((np.abs(xcam_int_g - xcam_int_b) > self._xcam_bg_threshold) & (xcam_int_g > self._xcam_bg_activation)) |\
               ((np.abs(xcam_int_r - xcam_int_g) < self._xcam_rg_threshold) & (xcam_int_g > self._xcam_rg_activation))

        output[mask] = [0, 0, 0]

        non_black_pixels_mask = np.any(output != [0, 0, 0], axis=-1)
        output[non_black_pixels_mask] = [255, 255, 255]

        output_1d = output.flatten()

        as64.xcam_percent = np.count_nonzero(output_1d) / output_1d.size

        if as64.xcam_percent > self._xcam_threshold and output[int(self._xcam_point_x_ratio*self._xcam_region_width), int(self._xcam_point_y_ratio*self._xcam_region_height), 2] > 20:
            as64.in_xcam = True
            if as64.current_time - self._xcam_found_time > 0.5:
                as64.xcam_count += 1

            self._xcam_found_time = as64.current_time
        else:
            as64.in_xcam = False
            self._split_on_current_xcam = False

    def analyze_fade_status(self):
        star_region = self._game_capture.get_region(STAR_REGION)
        life_region = self._game_capture.get_region(LIFE_REGION)

        # Determine the current fade status
        if is_black(star_region, self._black_threshold) and is_black(life_region, self._black_threshold):
            if as64.fade_status == NO_FADE and self._count_fades:
                as64.fadeout_count += 1
                as64.xcam_count = 0

            if is_black(self._game_capture.get_region(RESET_REGION), self._black_threshold) and as64.current_time - self._fade_start_time > self._minimum_fadeout_time:
                as64.fade_status = FADEOUT_COMPLETE
            else:
                as64.fade_status = FADEOUT_PARTIAL
        elif is_white(star_region, self._white_threshold) and is_white(life_region, self._white_threshold):
            if as64.fade_status == NO_FADE and self._count_fades:
                as64.fadein_count += 1
                as64.xcam_count = 0

            if not is_white(self._game_capture.get_region(FADEIN_REGION), self._white_threshold):
                as64.fade_status = FADEIN_COMPLETE
            else:
                as64.fade_status = FADEIN_PARTIAL
        else:
            as64.fade_status = NO_FADE
            self._fade_start_time = as64.current_time

    def _analyze_star_count_probability_mode(self):
        try:
            as64.prediction_info = self._model.predict(cv2.resize(convert_to_cv2(self._game_capture.get_region(STAR_REGION)), (self._model.width, self._model.height)))
        except cv2.error:
            self._error_occurred("An error occurred while processing " + config.get("game", "process_name"))
            return

        total_predictions = len(self._predictions)

        if as64.star_count - 1 <= as64.prediction_info.prediction <= as64.star_count + 1 or as64.prediction_info.prediction > 120:
            self._predictions.append(as64.prediction_info)

            # Limit number of predictions
            if total_predictions > self._prediction_processing_length:
                self._predictions.pop(0)

            # Handle Prediction
            prev_two_probabilities = [self._predictions[i].probability for i in range(total_predictions - 2, total_predictions)
                                      if self._predictions[i].prediction == as64.star_count + 1]

            try:
                result = next(x for x, val in enumerate(prev_two_probabilities) if val >= self._probability_threshold)

                if prev_two_probabilities[result ^ 1] >= self._confirmation_threshold:
                    self.set_star_count(as64.star_count + 1)
                    if as64.in_xcam:
                        as64.xcam_count = 1
            except (StopIteration, IndexError):
                pass

        self._star_error_check()

    def _analyze_star_count_confirmation_mode(self):
        try:
            as64.prediction_info = self._model.predict(cv2.resize(convert_to_cv2(self._game_capture.get_region(STAR_REGION)), (self._model.width, self._model.height)))
        except cv2.error:
            self._error_occurred("An error occurred while processing " + config.get("game", "process_name"))
            return

        total_predictions = len(self._predictions)

        if as64.star_count - 1 <= as64.prediction_info.prediction <= as64.star_count + 1 or as64.prediction_info.prediction > 120:
            self._predictions.append(as64.prediction_info)

            # Limit number of predictions
            if total_predictions > self._prediction_processing_length:
                self._predictions.pop(0)

            if as64.prediction_info.prediction == as64.star_count + 1 and as64.prediction_info.probability > self._confirmation_threshold:
                if as64.current_time - self._xcam_found_time < 1:
                    self.set_star_count(as64.star_count + 1)

        self._star_error_check()

    def _star_error_check(self):
        # Error Check
        # TODO: Handle fadeouts correctly. See below.
        # If split is undone, need to get previous fadeout count, set it to current, and add the fadeout count of the
        # incorrect star
        prev_star_probabilities = [p.probability for p in self._predictions if p.prediction == as64.star_count - 1]

        if len(prev_star_probabilities) >= self._minimum_undo_count:
            if sum(prev_star_probabilities) / len(prev_star_probabilities) > self._undo_prediction_threshold:
                self.set_star_count(as64.star_count - 1)

                try:
                    if as64.star_count < self._route.splits[self.split_index() - 1].star_count:
                        self.undo()
                except IndexError:
                    pass

        try:
            if self._star_skip_enabled and as64.previous_split_initial_star <= as64.prediction_info.prediction <= as64.next_split_split_star or as64.prediction_info.prediction > 120:
                if as64.prediction_info.prediction == self._previous_prediction.prediction and as64.prediction_info.probability > self._probability_threshold:
                    self._matching_consecutive_predictions += 1
                elif self._matching_consecutive_predictions > 0:
                    self._matching_consecutive_predictions = 0

                if self._matching_consecutive_predictions >= self._minimum_consecutive_predictions and 0 < abs(as64.prediction_info.prediction - as64.star_count) <= self._max_star_skip:
                    self.set_star_count(as64.prediction_info.prediction)

                    try:
                        if as64.star_count < self._route.splits[self.split_index() - 1].star_count:
                            self.undo()
                    except IndexError:
                        pass
        except AttributeError:
            pass

        self._previous_prediction = as64.prediction_info

    def get_region(self, region):
        return self._game_capture.get_region(region)

    def get_region_rect(self, region):
        return self._game_capture.get_region_rect(region)

    def register_split_processor(self, split_type, processor):
        self._processor_switch.register_processor(split_type, processor)

    #
    # TIMER FUNCTIONS
    #

    def split(self):
        # Cool-down period between splits
        if time.time() - as64.last_split < self._split_cooldown:
            return

        # Prevent splitting past the final split
        if self.split_index() == len(self._route.splits):
            return

        # Prevent splitting twice on one X-Cam
        if self._split_on_current_xcam:
            return
        else:
            self._split_on_current_xcam = True

        livesplit.split(self._ls_socket)
        as64.last_split = time.time()

    def reset(self):
        livesplit.reset(self._ls_socket)

        self.set_star_count(self._route.initial_star)
        as64.xcam_count = 0
        self._intro_ended = False
        self._split_on_current_xcam = False

    def skip(self):
        livesplit.skip(self._ls_socket)

    def undo(self):
        livesplit.undo(self._ls_socket)

    #
    # INFO FUNCTIONS
    #

    def current_split(self):
        return self._current_split

    def split_index(self):
        """ Return the current split index """
        try:
            return self._route.splits.index(self._current_split)
        except ValueError:
            print("ValueError: Current Split not found..")

    def incoming_split(self, star_count=True, fadeout=True, fadein=True):
        if as64.star_count != self._current_split.star_count and star_count:
            return False

        # TODO: Make only one fade need to match
        if as64.fadeout_count != self._current_split.on_fadeout and fadeout:
            return False

        if as64.fadein_count != self._current_split.on_fadein and fadein:
            return False

        return True

    #
    # TRACKING FUNCTIONS
    #

    def enable_predictions(self, enable):
        self._make_predictions = enable

    def enable_fade_count(self, enable):
        self._count_fades = enable
        self._reset_fade_count()

    def enable_xcam_count(self, enable):
        self._count_xcams = enable

        if not enable:
            self._split_on_current_xcam = False

    def set_intro_ended(self, ended):
        self._intro_ended = ended

    def set_star_count(self, star_count):
        self._reset_fade_count()
        as64.xcam_count = 0
        as64.star_count = star_count
        as64.collection_time = time.time()
        self._update_occurred()
        self._predictions = [PredictionInfo(0, 0)] * self._prediction_processing_length

    def set_split_index(self, index):
        try:
            self._current_split = self._route.splits[index]

            self._reset_fade_count()
            as64.xcam_count = 0

            try:
                as64.previous_split_initial_star = self._route.splits[self.split_index() - 2].star_count
            except IndexError:
                pass

            try:
                as64.next_split_split_star = self._route.splits[self.split_index() + 1].star_count
            except IndexError:
                pass

            self._update_occurred()
        except IndexError:
            pass

    #
    # HELPER FUNCTIONS
    #
    def set_update_listener(self, listener):
        self._update_listener = listener

    def set_error_listener(self, listener):
        self._error_listener = listener

    def _error_occurred(self, error):
        try:
            self._error_listener(error)
        except AttributeError:
            pass

        self.stop()

    def _update_occurred(self):
        try:
            self._update_listener(self.split_index(), as64.star_count, self.current_split().star_count)
        except AttributeError:
            pass

    def _reset_fade_count(self):
        as64.fadeout_count = 0
        as64.fadein_count = 0
