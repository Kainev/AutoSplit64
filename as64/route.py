import toml

from as64.constants import Version, SplitType

class RouteToken(object):
    ROUTE = "__route__"
    TITLE = "title"
    CATEGORY = "category"
    VERSION = "version"
    INITIAL_STAR = "initial_star"
    SPLITS = "SPLIT"
    LOGIC_PLUGIN = "logic_plugin"

class SplitToken(object):
    STAR_COUNT = "star_count"
    FADEOUT = "fade_out"
    FADEIN = "fade_in"
    XCAM = "x_cam"
    SPLIT_TYPE = "split_type"
    

class Route(object):
    def __init__(self, title: str, splits: list, initial_star: int=0, version: Version=Version.JP, category: str="", logic_plugin: str="_system"):
        self.title: str = title
        self.splits: list = splits
        self.initial_star: int = initial_star
        self.version: Version = version
        self.category: str = category
        self.logic_plugin: str = logic_plugin

class Split(object):
    def __init__(self, title: str="", star_count: int=0, fadeout: int = 0, fadein: int=0, xcam: int=-1, split_type: SplitType=SplitType.STAR):
        self.title: str = title
        self.star_count: int = star_count
        self.fadeout: int = fadeout
        self.fadein: int = fadein
        self.xcam: int = xcam
        self.split_type: SplitType = split_type
        
        
def load(file_path: str):
    try:
        with open(file_path) as file:
            return decode(toml.load(file))
    except FileNotFoundError as e:
        print("FileNotFound", e)
    except PermissionError as e:
        print("PermissionError", e)
    except toml.TomlDecodeError as e:
        print("DecoderError", e)
        
    # TODO: Raise custom exceptions

def save(route: Route, file_path: str):
    pass

def decode(data) -> Route:
    if RouteToken.ROUTE not in data:
        return None
    
    splits = []
    
    for key in data[RouteToken.SPLITS]:
        split = Split(title=key,
                      star_count=data[RouteToken.SPLITS][key][SplitToken.STAR_COUNT],
                      fadeout=data[RouteToken.SPLITS][key][SplitToken.FADEOUT],
                      fadein=data[RouteToken.SPLITS][key][SplitToken.FADEIN],
                      xcam=data[RouteToken.SPLITS][key][SplitToken.XCAM],
                      split_type=SplitType[data[RouteToken.SPLITS][key][SplitToken.SPLIT_TYPE]])
        
        splits.append(split)
        
    route = Route(title=data[RouteToken.TITLE],
                  splits=splits,
                  initial_star=data[RouteToken.INITIAL_STAR],
                  version=Version[data[RouteToken.VERSION]],
                  category=data[RouteToken.CATEGORY],
                  logic_plugin=data[RouteToken.LOGIC_PLUGIN])
    
    return route
        