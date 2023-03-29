import json
import copy


_config = {}
_defaults = None
_rollback = None

_CONFIG_FILE_NAME = "config.ini"
_DEFAULTS_FILE_NAME = "defaults.ini"


def add_section(section):
    global _config

    _config[section] = {}


def remove_section(section):
    global _config

    return _config.pop(section)


def add_key(section, key, value=None):
    global _config

    _config[section][key] = value


def remove_key(section, key):
    global _config
    return _config[section].pop(key)


def get(section, key=None):
    global _config

    if not _config:
        load_config()

    try:
        if key:
            return _config[section][key]
        else:
            return _config[section]
    except KeyError:
        if key:
            return get_default(section, key)
        else:
            return get_default(section)


def get_default(section, key=None):
    global _defaults

    if not _defaults:
        load_defaults()

    try:
        if key:
            return _defaults[section][key]
        else:
            return _defaults[section]
    except KeyError:
        return None


def set_key(section, key, value):
    global _config

    if section not in _config:
        _config[section] = {}

    if key not in _config[section]:
        _config[section][key] = value

    if section in _config:
        if key in _config[section]:
            _config[section][key] = value
        else:
            raise KeyError
    else:
        _config[section] = {}
        _config[section][key] = value


def set_section(section, value):
    global _config
    if section in _config:
        _config[section] = value
    else:
        raise KeyError


def create_rollback():
    global _rollback
    _rollback = copy.deepcopy(_config)


def rollback():
    if _rollback:
        global _config
        _config = copy.deepcopy(_rollback)


def flush_rollback():
    global _rollback
    rb = _rollback
    _rollback = None
    return rb


def load_config():
    global _config
    try:
        with open(_CONFIG_FILE_NAME) as file:
            data = json.load(file)
            _config = data
    except FileNotFoundError:
        generate_config()


def load_defaults():
    global _defaults
    with open(_DEFAULTS_FILE_NAME) as file:
        data = json.load(file)
        _defaults = data


def save_config():
    global _config

    # Save config.ini file
    with open(_CONFIG_FILE_NAME, 'w') as file:
        json.dump(_config, file, indent=4)

    # Remove rollback
    flush_rollback()


def generate_config():
    global _config

    load_defaults()
    _config = copy.deepcopy(_defaults)
    save_config()
