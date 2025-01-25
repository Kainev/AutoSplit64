# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import os
import sys
import logging
import inspect
import importlib.util
from typing import Optional, Type, List, Dict

from as64 import config

from .metadata import PluginMetaData

from .base import (
    BasePlugin,
    LifecyclePlugin,
    RealtimePlugin,
    GameStatePlugin,
    CapturePlugin,
    SplitPlugin
)


logger = logging.getLogger(__name__)


class DiscoveredPlugin:
    """
    A small struct to hold data about discovered plugins before final registration/loading.
    """
    def __init__(self, cls: Type[BasePlugin]):
        self.cls = cls

        if hasattr(cls, 'metadata') and isinstance(cls.metadata, PluginMetaData):
            self.name = cls.metadata.name
            self.version = cls.metadata.version
            self.dependencies = cls.metadata.required_plugins
        else:
            # Fallback if plugin lacks metadata
            fallback_name = cls.__name__
            self.name = fallback_name
            self.version = "0.0.0"
            self.dependencies = []

            cls.metadata = PluginMetaData(
                name=fallback_name,
                version="0.0.0"
            )
        
        self.category: Optional[str] = None


class PluginManager:
    """
    Manages plugin discovery and lifecycle
    """

    CATEGORY_MAPPING = {
        "game_state": GameStatePlugin,
        "realtime": RealtimePlugin,
        "lifecycle": LifecyclePlugin,
        "capture": CapturePlugin,
        "split": SplitPlugin,
    }

    def __init__(
        self,
        plugins_directory: str,
    ):
        """
        :param plugins_directory: Path containing subfolders for each plugin
        """
        self.plugins_directory = plugins_directory

        # Lifecycle plugin instances
        self.lifecycle_plugins: List[LifecyclePlugin] = []
        self.realtime_plugins: List[RealtimePlugin] = []
        self.game_state_plugins: List[GameStatePlugin] = []

        # On-demand plugin classes
        self.capture_plugin_class: Optional[Type[CapturePlugin]] = None
        self.split_plugin_class: Optional[Type[SplitPlugin]] = None

        #
        self.plugin_class_map: Dict[str, Type[BasePlugin]] = {}

    @staticmethod
    def is_subclass_of(cls, base_cls) -> bool:
        return (
            inspect.isclass(cls) and
            issubclass(cls, base_cls) and
            (cls is not base_cls)
        )

    def _import_module_from_file(self, module_name: str, file_path: str):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            raise ImportError(f"[PluginManager._import_module_from_file] Cannot load spec for {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _discover_plugins(self) -> List[DiscoveredPlugin]:
        discovered: List[DiscoveredPlugin] = []

        try:
            folders = [
                d for d in os.listdir(self.plugins_directory)
                if os.path.isdir(os.path.join(self.plugins_directory, d))
            ]
        except FileNotFoundError:
            logger.error(f"[_discover_plugins] Plugins directory not found: {self.plugins_directory}")
            return []

        for folder_name in folders:
            plugin_py = os.path.join(self.plugins_directory, folder_name, "plugin.py")
            if not os.path.isfile(plugin_py):
                logger.debug(f"[_discover_plugins] Skipping {folder_name}: no plugin.py found.")
                continue

            module_name = f"plugins.{folder_name}.plugin"
            try:
                module = self._import_module_from_file(module_name, plugin_py)
            except Exception as e:
                logger.error(f"[_discover_plugins] Failed to import plugin module {module_name}: {e}")
                continue

            # Find plugin classes
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue
                if not issubclass(cls, BasePlugin):
                    continue

                dp = DiscoveredPlugin(cls)

                # Determine plugin category
                for cat, base_cls in self.CATEGORY_MAPPING.items():
                    if self.is_subclass_of(cls, base_cls):
                        dp.category = cat
                        break

                if dp.category:
                    discovered.append(dp)
                else:
                    logger.warning(f"[_discover_plugins] Discovered plugin {cls.__name__} but could not map to a known category.")

        return discovered

    def _register_plugins(self, discovered: List[DiscoveredPlugin]) -> None:
        updated_config = False

        for dp in discovered:
            if not dp.category:
                continue

            plugin_list = config.get("plugins", dp.category, default=[])
                
            names_in_config = [p["plugin"] for p in plugin_list if "plugin" in p]

            if dp.name not in names_in_config:
                plugin_list.append({"plugin": dp.name, "loaded": True})
                config.set("plugins", dp.category, plugin_list)
                updated_config = True
                logger.info(f"[_register_plugins] Registered new plugin '{dp.name}' in category '{dp.category}'")

        if updated_config:
            config.save()

    def load_plugins(self) -> None:
        discovered = self._discover_plugins()

        if discovered:
            for dp in discovered:
                self.plugin_class_map[dp.name] = dp.cls
            self._register_plugins(discovered)
            
        for category in self.CATEGORY_MAPPING.keys():
            plugin_entries = config.get("plugins", category, default=[])

            for entry in plugin_entries:
                name = entry.get("plugin")
                loaded = entry.get("loaded", False)
                if not loaded:
                    logger.info(f"[load_plugins] Plugin '{name}' in category '{category}' is disabled. Skipping.")
                    continue

                cls = self.plugin_class_map.get(name)
                if not cls:
                    logger.error(f"[load_plugins] Configured plugin '{name}' not found among discovered classes.")
                    continue

                if category in ("lifecycle", "realtime", "game_state"):
                    self._instantiate_lifecycle_plugin(cls)
                elif category == "capture":
                    self._register_capture_plugin(cls)
                elif category == "split":
                    self._register_split_plugin(cls)


    def _instantiate_lifecycle_plugin(self, cls: Type[LifecyclePlugin]) -> None:
        try:
            instance = cls()
            if not instance.is_valid():
                logger.error(f"[_instantiate_lifecycle_plugin] Lifecycle plugin {cls.metadata.name} failed validation; skipping.")
                return

            if isinstance(instance, RealtimePlugin):
                self.realtime_plugins.append(instance)
            elif isinstance(instance, GameStatePlugin):
                self.game_state_plugins.append(instance)
            else:
                self.lifecycle_plugins.append(instance)

        except Exception as e:
            logger.error(f"[_instantiate_lifecycle_plugin] Could not instantiate {cls.metadata.name}: {e}", exc_info=True)

    def _register_capture_plugin(self, cls: Type[CapturePlugin]) -> None:
        if self.capture_plugin_class is not None:
            logger.warning(f"[_instantiate_lifecycle_plugin] Multiple capture plugins found; ignoring {cls.metadata.name}")
            return
        self.capture_plugin_class = cls
        logger.info(f"[_instantiate_lifecycle_plugin] Registered capture plugin: {cls.metadata.name}")

    def _register_split_plugin(self, cls: Type[SplitPlugin]) -> None:
        if self.split_plugin_class is not None:
            logger.warning(f"[_instantiate_lifecycle_plugin] Multiple split plugins found; ignoring {cls.metadata.name}")
            return
        self.split_plugin_class = cls
        logger.info(f"[_instantiate_lifecycle_plugin] Registered split plugin: {cls.metadata.name}")

    def initialize_lifecycle_plugins(self):
        for plugin in self.get_lifecycle_plugins():
            try:
                plugin.initialize()
                logger.info(f"[initialize_lifecycle_plugins] Initialized plugin {plugin.metadata.name}")
            except Exception as e:
                logger.error(f"[initialize_lifecycle_plugins] Error initializing plugin {plugin.metadata.name}: {e}")

    def start_lifecycle_plugins(self):
        for plugin in self.get_lifecycle_plugins():
            try:
                plugin.start()
                logger.info(f"[initialize_lifecycle_plugins] Started plugin {plugin.metadata.name}")
            except Exception as e:
                logger.error(f"[initialize_lifecycle_plugins] Error starting plugin {plugin.metadata.name}: {e}")

    def stop_lifecycle_plugins(self):
        for plugin in self.get_lifecycle_plugins():
            try:
                plugin.stop()
                logger.info(f"[initialize_lifecycle_plugins] Stopped plugin {plugin.metadata.name}")
            except Exception as e:
                logger.error(f"[initialize_lifecycle_plugins] Error stopping plugin {plugin.metadata.name}: {e}")

    def shutdown_lifecycle_plugins(self):
        for plugin in self.get_lifecycle_plugins():
            try:
                plugin.shutdown()
                logger.info(f"[initialize_lifecycle_plugins] Shutdown plugin {plugin.metadata.name}")
            except Exception as e:
                logger.error(f"[initialize_lifecycle_plugins] Error shutting down plugin {plugin.metadata.name}: {e}")

    def get_lifecycle_plugins(self) -> List[LifecyclePlugin]:
        return self.lifecycle_plugins + self.realtime_plugins + self.game_state_plugins
    
    def get_realtime_plugins(self) -> List[RealtimePlugin]:
        return self.game_state_plugins + self.realtime_plugins

    def get_capture_instance(self) -> Optional[CapturePlugin]:
        if not self.capture_plugin_class:
            logger.warning("[PluginManager] No capture plugin is registered.")
            return None
        try:
            instance = self.capture_plugin_class()
            if not instance.is_valid():
                logger.error(f"[PluginManager] Capture plugin {instance.metadata.name} is invalid.")
                return None
            return instance
        except Exception as e:
            logger.error(f"[PluginManager] Could not instantiate capture plugin: {e}", exc_info=True)
            return None

    def get_split_instance(self, state) -> Optional[SplitPlugin]:
        if not self.split_plugin_class:
            logger.warning("[PluginManager] No split plugin is registered.")
            return None
        try:
            instance = self.split_plugin_class(state)
            if not instance.is_valid():
                logger.error(f"[PluginManager] Split plugin {instance.metadata.name} is invalid.")
                return None
            return instance
        except Exception as e:
            logger.error(f"[PluginManager] Could not instantiate split plugin: {e}", exc_info=True)
            return None
