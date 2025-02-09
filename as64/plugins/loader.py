# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import sys
import inspect
import importlib.util
import logging
from typing import List

from .types import DiscoveredPlugin
from .base import BasePlugin

logger = logging.getLogger(__name__)

class PluginLoader:
    @staticmethod
    def import_module(module_name: str, file_path: str):
        """
        Imports a Python module given its name and the file path.
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def is_subclass_of(cls, base_cls) -> bool:
        """
        Returns True if cls is a subclass of base_cls (but not base_cls itself).
        """
        return inspect.isclass(cls) and issubclass(cls, base_cls) and (cls is not base_cls)

    @staticmethod
    def extract_plugins(module) -> List[DiscoveredPlugin]:
        """
        Scans a module for classes that are valid plugins (subclasses of BasePlugin) and
        assigns them a category (if category_order and category_mapping are provided).
        Returns a list of DiscoveredPlugin instances.
        """
        discovered: List[DiscoveredPlugin] = []
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue
            if not issubclass(cls, BasePlugin):
                continue
            dp = DiscoveredPlugin(cls)

            if dp.category:
                discovered.append(dp)
            else:
                logger.warning(f"[PluginLoader] Discovered plugin {cls.__name__} but could not map to a known category.")
        return discovered
