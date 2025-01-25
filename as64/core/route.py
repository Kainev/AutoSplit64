# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from os import path
import re
from typing import List
from xml.etree import ElementTree
import toml

from as64.enums import Version, SplitType


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
    def __init__(self, title: str, splits: list, initial_star: int=0, version: Version=Version.JP, category: str="", logic_plugin:str="_system"):
        self.title: str = title
        self.splits: list = splits
        self.initial_star: int = initial_star
        self.version: Version = version
        self.category: str = category
        self.logic_plugin: str = logic_plugin


class Split(object):
    def __init__(self, title: str="", star_count: int=0, fadeout: int = 0, fadein: int=0, xcam: int=-1, split_type: SplitType=None):
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
        
        
def save(route: Route, file_path: str):
    if not isinstance(route, Route):
        raise ValueError
    
    splits = {}
    
    for split in route.splits:
        splits[split.title] = {
            SplitToken.STAR_COUNT: split.star_count,
            SplitToken.FADEOUT: split.fadeout,
            SplitToken.FADEIN: split.fadein,
            SplitToken.XCAM: split.xcam,
            SplitToken.SPLIT_TYPE: split.split_type.name,
        }
    
    data = {
        RouteToken.ROUTE: True,
        RouteToken.TITLE: route.title,
        RouteToken.CATEGORY: route.category,
        RouteToken.INITIAL_STAR: route.initial_star,
        RouteToken.VERSION: route.version.name,
        RouteToken.LOGIC_PLUGIN: route.logic_plugin,
        RouteToken.SPLITS: splits
    }
    
    with open(file_path, 'w') as file:
        toml.dump(data, file)


def decode(data) -> Route:
    if RouteToken.ROUTE not in data:
        return None
    
    splits = []
    
    for key in data[RouteToken.SPLITS]:
        try:
            star_count = data[RouteToken.SPLITS][key][SplitToken.STAR_COUNT]
        except KeyError:
            star_count = None
            
        try:
            fadeout = data[RouteToken.SPLITS][key][SplitToken.FADEOUT]
        except KeyError:
            fadeout = None
            
        try:
            fadein = data[RouteToken.SPLITS][key][SplitToken.FADEIN]
        except KeyError:
            fadein = None
            
        try:
            xcam = data[RouteToken.SPLITS][key][SplitToken.XCAM]
        except KeyError:
            xcam = None

        split = Split(title=key,
                      star_count=star_count,
                      fadeout=fadeout,
                      fadein=fadein,
                      xcam=xcam,
                      split_type=SplitType[data[RouteToken.SPLITS][key][SplitToken.SPLIT_TYPE]])
        
        splits.append(split)
        
    print("SPLTS!", splits, flush=True)
        
    route = Route(title=data[RouteToken.TITLE],
                  splits=splits,
                  initial_star=data[RouteToken.INITIAL_STAR],
                  version=Version[data[RouteToken.VERSION]],
                  category=data[RouteToken.CATEGORY],
                  logic_plugin=data[RouteToken.LOGIC_PLUGIN])
    
    return route
        

BOWSER_TOKENS_MATCH = [
    'key',
    'bowser',
    
    'bitdw'
    'darkworld',
    'dark-world',
    'dark world',
    
    'bitfs',
    'firesea',
    'fire-sea',
    'fire sea'
]

BOWSER_TOKENS_EXACT = [
    'dw',
    'fs',
]

LBLJ_TOKENS = [
    'lblj'
]

UPSTAIRS_TOKENS_EXACT = [
    'up'
]

UPSTAIRS_TOKENS_MATCH = [
    'upstairs'
]

MIPS_TOKENS = [
    'mips',
    'bunny',
    'rabbit'
]

BLJ_TOKENS = [
    'bljs',
    'blj'
]


def translate_lss(file_path):
    try:
        if not path.exists(file_path):
            return None
    except ValueError:
        return None
    
    tree = ElementTree.parse(file_path)
    segments = tree.getroot().find('Segments')
    
    splits = []
    
    for index, segment in enumerate(segments):
        name = segment.find('Name').text
        delimited_name = name.lower().split()
          
        # Attempt to determine the star count
        numbers = re.findall(r'\d+', name)
        
        try:
            star_count = int(numbers[-1])
        except IndexError:
            star_count = None
            
        fadeout = None
        fadein = None
        xcam = None
            
        # --- Determine Split Type/Split values --- 
        if _match_token(name, BOWSER_TOKENS_MATCH) or _exact_token(delimited_name, BOWSER_TOKENS_EXACT):
            star_count = None
            split_type = SplitType.BOWSER
        elif _match_token(name, MIPS_TOKENS):
            star_count = None  
            split_type = SplitType.MIPS
        elif _match_token(name, LBLJ_TOKENS):
            split_type = SplitType.LBLJ   
        elif _match_token(name, UPSTAIRS_TOKENS_MATCH) or _exact_token(delimited_name, UPSTAIRS_TOKENS_EXACT):
            xcam = 1
            fadeout = 3
            split_type = SplitType.CUSTOM
        elif _match_token(name, BLJ_TOKENS):
            fadeout = 4   
            split_type = SplitType.CUSTOM 
        elif index == len(segments) - 1:
            star_count = None
            split_type = SplitType.BOWSER
        else:
            fadeout = 1
            split_type = SplitType.STAR
            
        splits.append(Split(
            title=name,
            star_count=star_count,
            fadeout=fadeout,
            fadein=fadein,
            xcam=xcam,
            split_type=split_type
        ))           
            
    # Find 
    final_star = None
    for i in range(len(splits) - 1, 0, -1):
        final_star = splits[i].star_count
        
        if final_star is not None:
            break
    
    if final_star == 0:
        category = '0 Star'
    elif final_star == 1:
        category = '1 Star'    
    elif final_star == 16:
        category = '16 Star'
    elif final_star in [69, 70]:
        category = '70 Star'
    elif final_star in [119, 120]:
        category = '120 Star'
    else:
        category = ''
        
    title = path.splitext(path.basename(file_path))[0]
        
    route = Route(
        title=title,
        splits=splits,
        initial_star=0,
        version=Version.AUTO,
        category=category,
        logic_plugin = 'RTA'
    )
    
    return route

    
def _match_token(name: str, tokens: List[str]) -> bool:
    for token in tokens:
        if name.lower().find(token) != -1:
            return True
        
    return False


def _exact_token(delimited_name: List[str], tokens: List[str]) -> bool:
    for token in tokens:
        if token in delimited_name:
            return True
    
    return False