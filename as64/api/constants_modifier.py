from aenum import extend_enum

from as64.constants import Event


def add_event_type(event_name: str) -> None:
    if event_name in Event.__dict__:
        # TODO: Raise Error
        return
    
    setattr(Event, event_name, event_name)
    


