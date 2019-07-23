import time
from threading import Thread

import cv2

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
    FADEIN_REGION
)


class Base(Thread):
    # TODO: Add all error messages to constants with associated error code
    def __init__(self, module):
        super().__init__()

        global as64
        as64 = module

        # Load config
        config.load_config()

        self._running = False
        self._count_fades = False
        self._make_predictions = True
        self._processor_switch = ProcessorSwitch()
        self._route = load_route(config.get("route", "path"))

        try:
            self._route_length = len(self._route.splits)
            self._current_split = self._route.splits[0]
        except AttributeError:
            self._route_length = 0
            self._current_split = None

        self._update_listener = None
        self._error_listener = None

        self._black_threshold = config.get("thresholds", "black_threshold")
        self._white_threshold = config.get("thresholds", "white_threshold")
        self._split_cooldown = config.get("general", "split_cooldown")
        self._probability_threshold = config.get("thresholds", "probability_threshold")
        self._confirmation_threshold = config.get("thresholds", "confirmation_threshold")
        self._prediction_processing_length = config.get("error", "processing_length")
        self._undo_prediction_threshold = config.get("error", "undo_threshold")
        self._minimum_undo_count = config.get("error", "minimum_undo_count")
        self._predictions = [PredictionInfo(0, 0)] * self._prediction_processing_length

        self._ls_socket = livesplit.init_socket()

        # Connect to LiveSplit
        livesplit.connect(self._ls_socket)

        # Initialize Game Capture
        if config.get("game", "override_version"):
            version = config.get("game", "version")
        else:
            try:
                version = self._route.version
            except AttributeError:
                version = config.get("route", "path")

        self._game_capture = GameCapture(config.get("game", "process_name"), config.get("game", "game_region"), version)

        # Initialise Model
        self._model = Model(config.get("model", "path"), config.get("model", "width"), config.get("model", "height"))

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
            self._error_occurred("Capture windows dimensions have changed since last configuring coordinates. Please reconfigure capture coordinates.")
            # TODO: Decide if we should then save the current capture dimensions so if they want to force the splitter to run like this they can.. but why would you need to?
            return False

        if not livesplit.check_connection(self._ls_socket):
            self._error_occurred("Could not connect to LiveSplit.")
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
        self._running = True

        valid = self.validity_check()

        if not valid:
            self.stop()

        self._processor_switch._current_processor = self._current_split.split_type

        while self._running:
            c_time = time.time()

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

            try:
                self._processor_switch.execute(self._current_split.split_type)
            except ConnectionAbortedError:
                self._error_occurred("LiveSplit connection failed")

            try:
                execution_time = time.time() - c_time
                time.sleep(1 / as64.fps - execution_time)
            except ValueError:
                pass

    def analyze_fade_status(self):
        star_region = self._game_capture.get_region(STAR_REGION)
        life_region = self._game_capture.get_region(LIFE_REGION)

        # Determine the current fade status
        if is_black(star_region, self._black_threshold) and is_black(life_region, self._black_threshold):
            if as64.fade_status == NO_FADE and self._count_fades:
                as64.fadeout_count += 1

            if is_black(self._game_capture.get_region(RESET_REGION), self._black_threshold):
                as64.fade_status = FADEOUT_COMPLETE
            else:
                as64.fade_status = FADEOUT_PARTIAL
        elif is_white(star_region, self._white_threshold) and is_white(life_region, self._white_threshold):
            if as64.fade_status == NO_FADE and self._count_fades:
                as64.fadein_count += 1

            if not is_white(self._game_capture.get_region(FADEIN_REGION), self._white_threshold):
                as64.fade_status = FADEIN_COMPLETE
            else:
                as64.fade_status = FADEIN_PARTIAL
        else:
            as64.fade_status = NO_FADE

    def analyze_star_count(self):
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
            except (StopIteration, IndexError):
                pass

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
            else:
                return

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
        if time.time() - as64.last_split < self._split_cooldown:
            return

        if self.split_index() == len(self._route.splits):
            return

        livesplit.split(self._ls_socket)
        as64.last_split = time.time()

    def reset(self):
        livesplit.reset(self._ls_socket)

        self.set_star_count(self._route.initial_star)

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

    def incoming_split(self):
        if as64.star_count != self._current_split.star_count:
            return False

        # TODO: Make only one fade need to match
        if as64.fadeout_count != self._current_split.on_fadeout:
            return False

        if as64.fadein_count != self._current_split.on_fadein:
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

    def set_star_count(self, star_count):
        self._reset_fade_count()
        as64.star_count = star_count
        as64.collection_time = time.time()
        self._update_occurred()
        self._predictions = [PredictionInfo(0, 0)] * self._prediction_processing_length
        print("Star Set:", as64.star_count)

    def set_split_index(self, index):
        try:
            self._current_split = self._route.splits[index]
            self._reset_fade_count()
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
