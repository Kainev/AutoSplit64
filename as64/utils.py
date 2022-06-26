

import os
import sys


def sublist_comparator(element, sublist):
    try:
        return sublist.index(element)
    except ValueError:
        return len(sublist)
    
    
def resource_path(relative_path):
    try:
        path = sys._MEIPASS
    except Exception:
        path = os.path.abspath(".")
        
    return os.path.join(path, relative_path).replace('\\', '/')


def calculate_point_from_ratio(region_size: list, point_ratio: list) -> list:
    return [
        int(round(region_size[0] * point_ratio[0])),
        int(round(region_size[1] * point_ratio[1]))
    ]