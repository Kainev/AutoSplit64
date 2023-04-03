import os
import sys
import inspect
from importlib import import_module

from as64.plugin.plugin import BasePlugin, Plugin
from as64 import utils


def is_plugin_subclass(cls) -> bool:
    """Determines if class is a BasePlugin subclass, but NOT the BasePlugin class itself

    Returns:
        bool: Does given class subclass BasePlugin
    """
    try:
        return issubclass(cls, BasePlugin) and cls != BasePlugin
    except Exception:
        return False


def import_plugin(plugin_file: str):
    module_path = os.path.splitext(plugin_file)[0].replace("\\", "/").replace("/", ".")

    _module = import_module(module_path)
    _plugin = None

    # Find BasePlugin subclasses in modules
    for name, cls in inspect.getmembers(sys.modules[_module.__name__], is_plugin_subclass):
        if cls == Plugin:
            continue

        if _plugin is not None:
            print("Multiple plugins detected")  # Todo: Make this error

        _plugin = cls

    return _plugin


def import_plugins(directory: str, order: list = [], include: list = None, exclude: list = []) -> list:
    """Import all modules from a given directory and return a list of found `BasePlugin` subclasses.

    Args:
        directory (str): Import directory
        order (list, optional): List of module names to order imports by. This can be a subset of found plugins, remaining modules will import last. Defaults to [].
        include (list, optional):
        exclude (list, optional): List of modules to ignore. Defaults to [].

    Returns:
        list: BasePlugin subclasses
    """
    # Find all modules in a given directory, sort by given order
    files = [file_name.split(".")[0] for file_name in os.listdir(directory) if file_name.endswith(".py") or file_name.endswith(".pyd")]
    files.sort(key=lambda element: utils.sublist_comparator(element, order))

    if include is not None:
        files = [file_name for file_name in files if file_name in include]

    package_path = directory.replace("/", ".")

    # BasePlugin Classes
    _plugins = []
    # Import plugins
    for file in files:
        # Don't import excluded plugins
        if file in exclude:
            continue

        _module = import_module("{}.{}".format(package_path, file))

        # Find BasePlugin subclasses in modules
        for name, cls in inspect.getmembers(sys.modules[_module.__name__], is_plugin_subclass):
            if cls == Plugin:
                continue

            _plugins.append(cls)

    return _plugins


def initialize_plugins(classes: list) -> list:
    """Initialize plugin instances and call plugin initialize method.

    Args:
        classes (list): BasePlugin classes to initialize.

    Returns:
        list: BasePlugin instances
    """
    # Initialized plugin instances
    instances = []

    for cls in classes:
        plugin = cls()
        plugin.initialize(None)

        instances.append(plugin)

    return instances


def initialize_plugin(cls):
    """Initialize plugin instance and call plugin initialize method.
    """
    # Initialized plugin instances
    _plugin = cls()
    _plugin.initialize(None)

    return _plugin
