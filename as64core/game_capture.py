from . import capture_shmem
from . import capture_window

from .constants import (
    GAME_US,
    GAME_REGION_BASE,
    GAME_REGION_RATIO,
    STAR_REGION_US_RATIO,
    STAR_REGION_JP_RATIO,
    LIFE_REGION_US_RATIO,
    LIFE_REGION_JP_RATIO,
    FADEOUT_REGION_RATIO,
    FADEIN_REGION_RATIO,
    RESET_REGION_RATIO,
    NO_HUD_REGION_RATIO,
    POWER_REGION_RATIO,
    XCAM_REGION_RATIO,
    GAME_REGION,
    STAR_REGION,
    LIFE_REGION,
    FADEOUT_REGION,
    FADEIN_REGION,
    RESET_REGION,
    NO_HUD_REGION,
    POWER_REGION,
    XCAM_REGION
)


class GameCapture(object):
    def __init__(self, use_obs, process_name, game_region, version):
        # Initialize GameCapture
        self._use_obs = use_obs
        self._process_name = process_name
        
        if self._use_obs:
        # Initialize SharedMemoryCapture
            self._shmem = capture_shmem.SharedMemoryCapture()
        else:
            self._hwnd: int = capture_window.get_hwnd_from_list(process_name, capture_window.get_visible_processes())
        
        
        self._game_region: list = game_region
        self._version = version

        self._regions: dict = {}
        self._window_image = None
        self._region_images: dict = {}

        self._add_default_regions()

    def _add_default_regions(self):
        """ Add default regions as per constants """
        def calc_ratio(c: list, b: list) -> list:
            return [c[0] / b[0], c[1] / b[1], c[2] / b[0], c[3] / b[1]]

        def calc_region(ratio: list) -> list:
            """ Convert a region expressed as a ratio into absolute coordinates """
            return [int(round(self._game_region[0] + (self._game_region[2] * ratio[0]))),
                    int(round(self._game_region[1] + (self._game_region[3] * ratio[1]))),
                    int(round(self._game_region[2] * ratio[2])),
                    int(round(self._game_region[3] * ratio[3]))]

        if self._version == GAME_US:
            self._regions[STAR_REGION] = calc_region(calc_ratio(STAR_REGION_US_RATIO, GAME_REGION_BASE))
            self._regions[LIFE_REGION] = calc_region(calc_ratio(LIFE_REGION_US_RATIO, GAME_REGION_BASE))
        else:
            self._regions[STAR_REGION] = calc_region(calc_ratio(STAR_REGION_JP_RATIO, GAME_REGION_BASE))
            self._regions[LIFE_REGION] = calc_region(calc_ratio(LIFE_REGION_JP_RATIO, GAME_REGION_BASE))

        self._regions[GAME_REGION] = calc_region(calc_ratio(GAME_REGION_RATIO, GAME_REGION_BASE))
        self._regions[FADEOUT_REGION] = calc_region(calc_ratio(FADEOUT_REGION_RATIO, GAME_REGION_BASE))
        self._regions[FADEIN_REGION] = calc_region(calc_ratio(FADEIN_REGION_RATIO, GAME_REGION_BASE))
        self._regions[RESET_REGION] = calc_region(calc_ratio(RESET_REGION_RATIO, GAME_REGION_BASE))
        self._regions[NO_HUD_REGION] = calc_region(calc_ratio(NO_HUD_REGION_RATIO, GAME_REGION_BASE))
        self._regions[POWER_REGION] = calc_region(calc_ratio(POWER_REGION_RATIO, GAME_REGION_BASE))
        self._regions[XCAM_REGION] = calc_region(calc_ratio(XCAM_REGION_RATIO, GAME_REGION_BASE))

    def is_valid(self):
        if self._use_obs:
            try:
                self._shmem.open_shmem()
            except Exception as e:
                raise Exception(str(e))    
        else:
            if not bool(self._hwnd):
                raise Exception("Could not capture " + self._process_name)

    def capture(self) -> None:
        if self._use_obs:
            try:
                self._window_image = self._shmem.capture()
            except Exception as e:
                raise Exception(str(e)) 
        else:
            self._window_image = capture_window.capture(self._hwnd) 
        self._region_images = {}  

    def get_capture_size(self):
        if self._use_obs:
            return self._shmem.get_capture_size()
        else:
            return capture_window.get_capture_size(self._hwnd)

    def get_region(self, region):
        if self._window_image is None:
            self.capture()

        try:
            return self._region_images[region]
        except KeyError:
            try:
                self._region_images[region] = self._crop(*self._regions[region])
                return self._region_images[region]
            except KeyError:
                return None

    def get_region_rect(self, region):
        try:
            return self._regions[region]
        except KeyError:
            return None

    def _crop(self, x, y, width, height):
        return self._window_image[y:y + height, x:x + width]
    
    # Destructor
    def close(self):
        if self._use_obs:
            self._shmem.close_shmem()

