# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from as64.core import (
    GameState,
    GameController
)


from as64.enums import (
    Event,
    FadeStatus,
    Region,
    SplitType,
    Camera
)


from as64.plugins import (
    Plugin,
    CapturePlugin,
    SplitPlugin,
    GameStatePlugin,
    PluginMetaData,
    PluginValidationError
)


from . import (
    config,
    emitter,
    windows,
    ipc,
    rpc,
    state,
    image,
    modifiers,
    math
)

from .state import (
    State,
    StateMachine
)

from .modifiers import (
    register_event
)


def get_game_state() -> GameState:
    pass

def get_game_controller() -> GameController:
    pass
