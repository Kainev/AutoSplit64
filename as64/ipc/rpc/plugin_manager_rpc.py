# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from as64.plugins import CapturePlugin
from as64.plugins.management import plugin_manager

from .registry import register

@register("plugin_manager.capture_plugins")
def capture_plugins():
    capture_plugins = plugin_manager.get_found_plugin_classes(CapturePlugin)
    return [cls.metadata.name for cls in capture_plugins]

@register("plugin_manager.current_capture_plugin")
def current_capture_plugin():
    return plugin_manager.get_active_plugin_classes(CapturePlugin).metadata.name

@register("plugin_manager.set_loaded")
def set_loaded(plugin_name: str, loaded: bool):
    plugin_manager.set_plugin_loaded_by_name(plugin_name, loaded)
    
@register("plugin_manager.available_capture_sources")
def available_capture_sources():
    capture_plugin = plugin_manager.get_active_plugin_classes(CapturePlugin)()
    return capture_plugin.get_available_sources()