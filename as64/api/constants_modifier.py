from aenum import extend_enum

from as64.constants import Event, SplitType


def add_event_type(event_name: str) -> None:
    if event_name in Event.__dict__:
        # TODO: Raise Error
        return
    
    setattr(Event, event_name, event_name)
    

def add_split_type(split_name: str) -> None:
    extend_enum(SplitType, split_name)
    

    


