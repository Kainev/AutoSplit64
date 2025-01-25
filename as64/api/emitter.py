# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from typing import Callable, Any
from pymitter import EventEmitter

_emitter: EventEmitter = None

def on(event: str, callback: Callable[..., Any]) -> None:
    _emitter.on(event, callback)

def off(event: str, callback: Callable[..., Any]) -> None:
    _emitter.off(event, callback)

def emit(event: str, *args: Any, **kwargs: Any) -> None:
    _emitter.emit(event, *args, **kwargs)
