from .constants import SPLIT_NORMAL, TIMING_RTA

FILE_PATH = "file_path"
ROUTE = "__route__"
TITLE = "title"
CATEGORY = "category"
INITIAL_STAR = "initial_star"
TIMING = "timing"
FINAL_STAR = "final_star"
FINAL_SPLIT = "final_split"
STAR_COUNT = "star_count"
VERSION = "version"
FADEOUT = "fade_out"
FADEIN = "fade_in"
XCAM = "xcam"
SPLIT_TYPE = "split_type"
SPLITS = "splits"
TIMEOUT = "timeout"
ICON = "icon_path"


class Route(object):
    def __init__(self, file_path, title, splits, initial_star=0, version="JP", category="", timing=TIMING_RTA):
        self.file_path = file_path
        self.title = title
        self.category = category
        self.splits = splits
        self.length = len(self.splits)
        self.initial_star = initial_star
        self.version = version
        self.timing = timing

    def insert_split(self, index):
        self.splits.insert(index, Split())

    def remove_split(self, index):
        self.splits.pop(index)


class Split(object):
    def __init__(self, title: str = "", star_count: int = 0, on_fadeout: int = 0, on_fadein: int = 0, on_xcam: int = -1, split_type: str = SPLIT_NORMAL, icon_path: str = None):
        self.title: str = title
        self.star_count: int = star_count
        self.on_fadeout: int = on_fadeout
        self.on_fadein: int = on_fadein
        self.on_xcam: int = on_xcam
        self.split_type: str = split_type
        self.icon_path: str = icon_path
