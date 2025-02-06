# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import toml
import copy
import threading
import logging
from typing import Any

from as64.ipc import rpc

logger = logging.getLogger(__name__)


_CONFIG_FILE_NAME = "config.toml"
_DEFAULTS_FILE_NAME = "defaults.toml"

_config = {}
_defaults = {}
_lock = threading.RLock()


def load() -> None:
    """Load configuration and defaults."""
    global _config, _defaults

    with _lock:        
        # Load defaults
        if os.path.exists(_DEFAULTS_FILE_NAME):
            try:
                with open(_DEFAULTS_FILE_NAME, "r") as file:
                    _defaults = toml.load(file)
                logger.debug(f"[config.load] Defaults loaded from {_DEFAULTS_FILE_NAME}")
            except Exception as e:
                logger.error(f"[config.load] Failed to load defaults from {_DEFAULTS_FILE_NAME}: {e}")
                raise RuntimeError(f"Failed to load defaults: {e}")
        else:
            logger.warning(f"[config.load] Defaults file {_DEFAULTS_FILE_NAME} not found. Using empty defaults.")
            _defaults = {}

        # Load user config
        if os.path.exists(_CONFIG_FILE_NAME):
            try:
                with open(_CONFIG_FILE_NAME, "r") as file:
                    _config = toml.load(file)
                logger.debug(f"[config.load] Configuration loaded from {_CONFIG_FILE_NAME}")
            except Exception as e:
                logger.error(f"[config.load] Failed to load configuration from {_CONFIG_FILE_NAME}: {e}")
                raise RuntimeError(f"Failed to load configuration: {e}")
        else:
            logger.warning(f"[config.load] Config file {_CONFIG_FILE_NAME} not found. Generating a new one.")
            _generate_config()

@rpc.register("config.save")
def save() -> None:
    """Save the current configuration to file."""
    global _config

    with _lock:
        try:
            with open(_CONFIG_FILE_NAME, "w") as file:
                toml.dump(_config, file)
            logger.debug(f"[config.save] Configuration saved to {_CONFIG_FILE_NAME}.")
        except Exception as e:
            logger.error(f"[config.save] Failed to save configuration to {_CONFIG_FILE_NAME}: {e}")
            raise RuntimeError(f"Failed to save configuration: {e}")

@rpc.register("config.get")
def get(*keys: str, default: Any = None) -> Any:
    """Get a nested configuration value."""
    global _config

    with _lock:
        value = _config
        for key in keys:
            if key in value:
                value = value[key]
            elif default is not None:
                return default
            else:
                logger.error(f"[config.get] Configuration key not found and no default set: {'.'.join(keys)}")
                raise KeyError(f"Configuration key not found and no default specified: {'.'.join(keys)}")
            
        logger.debug(f"[config.get] Retrieved {'.'.join(keys)}: {value}")
        return value

@rpc.register("config.set")
def set(*keys: Any) -> None:
    """Set a nested configuration value."""
    global _config

    with _lock:
        path = list(keys[:-1])
        value = keys[-1]
        key = path.pop() if path else None

        section = _config
        for part in path:
            if part in section and not isinstance(section[part], dict):
                logger.error(f"[config.set] Cannot set nested key under '{part}' for path '{'.'.join(keys)}': Not a dictionary")
                raise TypeError(f"Cannot set nested key under '{part}' for path '{'.'.join(keys)}': Not a dictionary")
            section = section.setdefault(part, {})

        if key:
            section[key] = value
            logger.info(f"[config.set] Configuration updated: {'.'.join(keys[:-1])}.{key} = {value}")


def _generate_config() -> None:
    """Generate initial configuration from defaults."""
    global _config, _defaults

    with _lock:
        _config = copy.deepcopy(_defaults)
        save()
        logger.info(f"[config._generate_config] New configuration generated and saved to {_CONFIG_FILE_NAME}.")
