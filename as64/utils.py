

def sublist_comparator(element, sublist):
    try:
        return sublist.index(element)
    except ValueError:
        return len(sublist)