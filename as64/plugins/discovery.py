# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os

from abc import (
    ABC,
    abstractmethod
)

from typing import (
    List,
)

from .types import DiscoveredPlugin
from .loader import PluginLoader


class IPluginDiscovery(ABC):
    @abstractmethod
    def discover(self) -> List[DiscoveredPlugin]:
        """Discover plugins and return a list of DiscoveredPlugin objects."""
        pass

class DirectoryPluginDiscovery(IPluginDiscovery):
    def __init__(self, plugins_directory: str, logger):
        self.plugins_directory = plugins_directory
        self.logger = logger

    def discover(self) -> List[DiscoveredPlugin]:
        discovered = []
        
        try:
            entries = os.listdir(self.plugins_directory)
        except FileNotFoundError:
            self.logger.error(f"Plugins directory not found: {self.plugins_directory}")
            return discovered

        for entry in entries:
            entry_path = os.path.join(self.plugins_directory, entry)
            
            if os.path.isdir(entry_path):
                plugin_py = os.path.join(entry_path, "plugin.py")
                
                if not os.path.isfile(plugin_py):
                    self.logger.debug(f"Skipping directory '{entry}': no plugin.py found.")
                    continue
                
                module_name = f"plugins.{entry}.plugin"
                try:
                    module = PluginLoader.import_module(module_name, plugin_py)
                except Exception as e:
                    self.logger.error(f"Failed to import module {module_name}: {e}")
                    continue

                discovered.extend(
                    PluginLoader.extract_plugins(module)
                )
                
        return discovered


class FilePluginDiscovery(IPluginDiscovery):
    def __init__(self, plugins_directory: str, logger):
        self.plugins_directory = plugins_directory
        self.logger = logger

    def discover(self) -> List[DiscoveredPlugin]:
        discovered = []
        
        try:
            entries = os.listdir(self.plugins_directory)
        except FileNotFoundError:
            self.logger.error(f"Plugins directory not found: {self.plugins_directory}")
            return discovered

        for entry in entries:
            entry_path = os.path.join(self.plugins_directory, entry)
            
            if os.path.isfile(entry_path) and entry.endswith(".py") and entry != "__init__.py":
                module_name = f"plugins.{entry[:-3]}"  # remove .py extension - TODO: do this properly
                
                try:
                    module = PluginLoader.import_module(module_name, entry_path)
                except Exception as e:
                    self.logger.error(f"Failed to import module {module_name}: {e}")
                    continue

                discovered.extend(
                    PluginLoader.extract_plugins(module)
                )
                
        return discovered