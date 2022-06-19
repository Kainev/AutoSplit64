import toml
import copy


# File Paths
_CONFIG_FILE_NAME = "config"
_DEFAULTS_FILE_NAME  = "defaults"

_config = {}
_defaults = {}
_rollbacks = {}


def get(*args):
    value = _config

    for section in args:
        value = value[section]

    return value


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

