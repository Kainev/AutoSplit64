# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from aenum import extend_enum

from as64.enums import (
    Event
)


def register_event(event: str) -> None:
    extend_enum(Event, event, event)
