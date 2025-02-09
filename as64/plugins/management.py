# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license


import logging
from typing import Type, List, Dict
from collections import defaultdict

from as64 import config

from .base import (
    BasePlugin,
    CapturePlugin,
    SplitPlugin
)

from .discovery import (
    DiscoveredPlugin,
    DirectoryPluginDiscovery,
    FilePluginDiscovery
)


logger = logging.getLogger(__name__)
   
        
class PluginManager:
    """
    Manages plugin discovery and lifecycle using a unified Plugin type.
    Supports plugins as either a plugin folder (with a plugin.py) or a standalone .py file.
    Also collects all discovered capture and split plugins for UI listing.
    """
    def __init__(self, plugins_directory: str):
        """
        :param plugins_directory: Path containing plugin subfolders and/or standalone .py files.
        """
        self.plugins_directory = plugins_directory
        
        self.discoverers = [
            DirectoryPluginDiscovery(plugins_directory, logger),
            FilePluginDiscovery(plugins_directory, logger)
        ]
        
        self.plugin_class_map: Dict[str, Type[BasePlugin]] = {}
        
        self.found_plugins: Dict[Type[BasePlugin], List[Type[BasePlugin]]] = defaultdict(list)
        self.active_plugins: Dict[Type[BasePlugin], List[Type[BasePlugin]]] = defaultdict(list)
        
        self.plugins: Dict[Type[BasePlugin], List[Type[BasePlugin]]] = defaultdict(list)

        self.SINGLE_INSTANCE_TYPES = { CapturePlugin, SplitPlugin }

    def _discover_plugins(self) -> List[DiscoveredPlugin]:
        discovered = []
        for discoverer in self.discoverers:
            discovered.extend(discoverer.discover())
        return discovered
    
    def _register_single_instance_plugin(self, dp: DiscoveredPlugin) -> None:
        plugin_entry = config.get("plugins", dp.category.__name__, default=None)
                
        if not plugin_entry:
            config.set("plugins", dp.category.__name__, {"plugin": dp.name, "loaded": True})            
            
    def _register_multi_instance_plugin(self, dp: DiscoveredPlugin) -> None:
        plugin_list = config.get("plugins", dp.category.__name__, default=[])
        names_in_config = [p["plugin"] for p in plugin_list if "plugin" in p]
                
        if dp.name not in names_in_config:
            plugin_list.append({"plugin": dp.name, "loaded": True})
            config.set("plugins", dp.category.__name__, plugin_list)
            logger.info(f"Registered new {dp.category.__name__} plugin '{dp.name}'")

    def _register_plugins(self, discovered: List[DiscoveredPlugin]) -> None:
        for dp in discovered:
            if dp.category is None:
                continue

            self.plugin_class_map[dp.name] = dp.cls
            self.found_plugins[dp.category].append(dp.cls)

            if dp.category in self.SINGLE_INSTANCE_TYPES:
                self._register_single_instance_plugin(dp)
            else:
                self._register_multi_instance_plugin(dp)
                
        config.save()

    def load_plugins(self) -> None:
        discovered = self._discover_plugins()
        if discovered:
            self._register_plugins(discovered)

        for category, plugins in self.found_plugins.items():
            if category in self.SINGLE_INSTANCE_TYPES:
                plugin_entry = config.get("plugins", category.__name__, default=None)
                if plugin_entry:
                    name = plugin_entry.get("plugin")
                    loaded = plugin_entry.get("loaded", False)
                    
                    if not loaded:
                        logger.info(f"{category.__name__} plugin '{name}' is disabled. Skipping.")
                        continue
                    
                    cls = self.plugin_class_map.get(name)
                    if not cls:
                        logger.error(
                            f"Configured {category.__name__} plugin '{name}' not found among discovered classes."
                        )
                        continue
                    
                    self.active_plugins[category] = cls
            else:
                plugin_entries = config.get("plugins", category.__name__, default=[])
                for entry in plugin_entries:
                    name = entry.get("plugin")
                    loaded = entry.get("loaded", False)
                    
                    if not loaded:
                        logger.info(f"{category.__name__} plugin '{name}' is disabled. Skipping.")
                        continue
                    
                    cls = self.plugin_class_map.get(name)
                    if not cls:
                        logger.error(f"Configured {category.__name__} plugin '{name}' not found.")
                        continue
                    
                    self.active_plugins[category].append(cls)
                    
    def get_active_plugin_classes(self, base_class: Type[BasePlugin]):
        return self.active_plugins[base_class]
    
    def get_found_plugin_classes(self, base_class: Type[BasePlugin]):
        return self.found_plugins[base_class]
    
    def get_plugin_instances(self, base_class: Type[BasePlugin]):
        return self.plugins[base_class]

    def _instantiate_plugin(self, cls: Type[BasePlugin]) -> None:
        try:
            instance = cls()
            if not instance.is_valid():
                logger.error(f"[_instantiate_plugin] Plugin {cls.metadata.name} failed validation; skipping.")
                return
            
            return instance
        except Exception as e:
            logger.error(f"[_instantiate_plugin] Could not instantiate plugin {cls.metadata.name}: {e}", exc_info=True)
            
    def instantiate_plugins(self, category: Type[BasePlugin]) -> None:
        already_instantiated_classes = {type(instance) for instance in self.plugins[category]}
        for cls in self.active_plugins[category]:
            if cls not in already_instantiated_classes:
                instance = self._instantiate_plugin(cls)
                self.plugins[category].append(instance)
            else:
                logger.debug(f"Skipping instantiation for {cls} since it already exists.")
                
        return 
                
    def run_method(
        self, 
        category_class: Type[BasePlugin], 
        method_name: str, 
        *args, 
        **kwargs
    ) -> None:
        """
        Call `method_name` on each plugin in the specified category, with optional positional
        and keyword arguments.
        """
        for instance in self.plugins[category_class]:
            method = getattr(instance, method_name, None)
            if callable(method):
                method(*args, **kwargs)
            else:
                logger.warning(
                    f"{instance.__class__.__name__} does not have a method '{method_name}'. Skipping."
                )
                
    def set_plugin_loaded_by_name(
        self,
        plugin_name: str,
        loaded: bool
    ) -> None:
        """
        Toggle (enable or disable) the 'loaded' status of a plugin
        by looking up its category from the discovered plugin info
        """
        cls = self.plugin_class_map.get(plugin_name)
        if not cls:
            logger.error(f"No plugin class found for name '{plugin_name}'.")
            return

        derived_category = None
        for cat, class_list in self.found_plugins.items():
            if cls in class_list:
                derived_category = cat
                break

        if not derived_category:
            logger.error(f"Could not determine category for '{plugin_name}'.")
            return

        if derived_category in self.SINGLE_INSTANCE_TYPES:
            self._set_single_instance_plugin_loaded(derived_category, plugin_name, loaded)
        else:
            self._set_multi_instance_plugin_loaded(derived_category, plugin_name, loaded)
            
    def _set_single_instance_plugin_loaded(
        self,
        category: Type[BasePlugin],
        plugin_name: str,
        loaded: bool
    ) -> None:
        plugin_entry = config.get("plugins", category.__name__, default=None)

        # If not in config, create it
        if not plugin_entry:
            plugin_entry = {"plugin": plugin_name, "loaded": loaded}
        else:
            plugin_entry["plugin"] = plugin_name
            plugin_entry["loaded"] = loaded

        config.set("plugins", category.__name__, plugin_entry)
        config.save()

        # Update in-memory data
        if loaded:
            self.active_plugins[category] = cls = self.plugin_class_map.get(plugin_name)
            if not cls:
                logger.error(f"Could not find plugin class for '{plugin_name}'")
                return
        else:
            self.active_plugins[category] = None  
            for instance in list(self.plugins[category]):
                if type(instance).__name__ == plugin_name:
                    self.plugins[category].remove(instance)

    def _set_multi_instance_plugin_loaded(
        self,
        category: Type[BasePlugin],
        plugin_name: str,
        loaded: bool
    ) -> None:
        plugin_list = config.get("plugins", category.__name__, default=[])

        # Find or create config entry
        found = False
        for entry in plugin_list:
            if entry.get("plugin") == plugin_name:
                entry["loaded"] = loaded
                found = True
                break
        if not found:
            plugin_list.append({"plugin": plugin_name, "loaded": loaded})

        config.set("plugins", category.__name__, plugin_list)
        config.save()

        cls = self.plugin_class_map.get(plugin_name)
        if not cls:
            logger.error(f"Could not find plugin class for '{plugin_name}'")
            return

        # Update active plugins
        if loaded:
            if cls not in self.active_plugins[category]:
                self.active_plugins[category].append(cls)
            # Optionally instantiate right away
            self.instantiate_plugins(category)
        else:
            if cls in self.active_plugins[category]:
                self.active_plugins[category].remove(cls)
            for instance in list(self.plugins[category]):
                if type(instance) == cls:
                    self.plugins[category].remove(instance)
    

plugin_manager = PluginManager("plugins")
