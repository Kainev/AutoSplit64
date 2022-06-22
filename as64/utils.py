

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