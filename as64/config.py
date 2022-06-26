from typing import Any
import toml
import copy


# File Paths
_CONFIG_FILE_NAME = "config.ini"
_DEFAULTS_FILE_NAME  = "defaults.ini"

_config = {}
_defaults = {}
_rollbacks = {}

# Event
_event_emitter = None


def get(*args) -> Any:
    """Get value from the currently loaded config file.

    Returns:
        Any: Value from config file
    """
    global _config
    value = _config


    for section in args:
        # TODO: Catch KeyError 
        value = value[section]

    return value


def set(*args) -> None:
    global _config

    path = list(args)
    print(path)
    value = path.pop()
    key = path.pop()

    current_section = _config

    for section in path:
        # TODO: Catch KeyError
        current_section = current_section[section]
    
    current_section[key] = value

    

def load():
    global _config
    global _defaults

    try:
        with open(_DEFAULTS_FILE_NAME) as file:
            _defaults = toml.load(file)
    except FileNotFoundError:
        pass # TODO: Can't generate defaults.. Raise an error?

    try:
        with open(_CONFIG_FILE_NAME) as file:
            _config = toml.load(file)
    except FileNotFoundError:
        _generate()


def save():
    global _config

    try:
        with open(_CONFIG_FILE_NAME, 'w') as file:
            toml.dump(_config, file)
            _rollbacks.clear()
    except FileNotFoundError:
        pass  # TODO: Handle error
    except PermissionError:
        pass  # TODO: Handle error
    
    
def _generate():
    global _config

    _config = copy.deepcopy(_defaults)
    save()

