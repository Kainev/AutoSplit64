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
from typing import Any, Dict

from as64.ipc import rpc

logger = logging.getLogger(__name__)


_CONFIG_FILE_NAME = "config.toml"
_DEFAULTS_FILE_NAME = "defaults.toml"

_config = {}
_defaults = {}
_rollbacks = {}
_lock = threading.RLock()

_NO_DEFAULT = object()

# Set externally
_enqueue_message = None


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
           
@rpc.register("config.create_rollback")  
def create_rollback(key: str) -> None:
    global _rollbacks
    _rollbacks[key] = copy.deepcopy(_config)
    
@rpc.register("config.rollback")
def rollback(id: str, *path: str) -> None:
    """
    Roll back either the entire config (if no path is given)
    or just the portion at the specified path.
    """
    global _rollbacks, _config
    with _lock:
        if id not in _rollbacks:
            raise KeyError(f"No rollback found for ID '{id}'.")

        if not path:
            _config = copy.deepcopy(_rollbacks[id])
            logger.info(f"[config.rollback] Entire config rolled back to ID '{id}'.")
        else:
            try:
                old_value = _get(_rollbacks[id], *path, default=_NO_DEFAULT)
            except KeyError:
                # Path didn't exist in the rollback snapshot, remove it from current config
                _delete(_config, *path)
                logger.info(f"[config.rollback] Path {'.'.join(path)} removed; it did not exist in rollback ID '{id}'.")
                return

            if old_value is _NO_DEFAULT:
                _delete(_config, *path)
                logger.info(f"[config.rollback] Path {'.'.join(path)} removed; it did not exist in rollback ID '{id}'.")
            else:
                _set(_config, *path, old_value)
                logger.info(f"[config.rollback] Path {'.'.join(path)} rolled back in config to ID '{id}'.")
                

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
def get(*keys: str, default: Any = _NO_DEFAULT) -> Any:
    """Get a nested configuration value."""
    global _config

    return _get(_config, *keys, default=default)


@rpc.register("config.set")
def set(*keys: Any) -> None:
    """Set a nested configuration value."""
    global _config
    _set(_config, *keys)
    _enqueue_message({
        "event": "config.update",
        "data": keys
    })
    
    
def _get(data, *keys: str, default: Any = _NO_DEFAULT) -> Any:
    with _lock:
        value = data
        for key in keys:
            if key in value:
                value = value[key]
            elif default is not _NO_DEFAULT:
                return default
            else:
                logger.error(f"[config.get] Configuration key not found and no default set: {'.'.join(keys)}")
                raise KeyError(f"Configuration key not found and no default specified: {'.'.join(keys)}")
            
        logger.debug(f"[config.get] Retrieved {'.'.join(keys)}: {value}")
        return value


def _set(data, *keys: Any) -> None:
    with _lock:
        path = list(keys[:-1])
        value = keys[-1]
        key = path.pop() if path else None

        section = data
        for part in path:
            if part in section and not isinstance(section[part], dict):
                logger.error(f"[config.set] Cannot set nested key under '{part}' for path '{'.'.join(keys)}': Not a dictionary")
                raise TypeError(f"Cannot set nested key under '{part}' for path '{'.'.join(keys)}': Not a dictionary")
            section = section.setdefault(part, {})

        if key:
            section[key] = value
            logger.info(f"[config.set] Configuration updated: {'.'.join(keys[:-1])}.{key} = {value}")
            
            
def _delete(data: Dict[str, Any], *keys: str) -> None:
    """
    Delete a nested key from `data`. 
    If any part of the path doesn't exist, it's a no-op.
    """
    with _lock:
        if not keys:
            return
        *parts, last_part = keys
        section = data
        for part in parts:
            if part not in section or not isinstance(section[part], dict):
                # Path doesn't exist, nothing to remove
                return
            section = section[part]

        if last_part in section:
            del section[last_part]
            logger.debug(f"[config._delete] Key path {'.'.join(keys)} removed.")
        else:
            logger.debug(f"[config._delete] Key path {'.'.join(keys)} does not exist; nothing to remove.")



    

def _generate_config() -> None:
    """Generate initial configuration from defaults."""
    global _config, _defaults

    with _lock:
        _config = copy.deepcopy(_defaults)
        save()
        logger.info(f"[config._generate_config] New configuration generated and saved to {_CONFIG_FILE_NAME}.")
