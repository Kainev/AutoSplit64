# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from abc import ABC, abstractmethod
from typing import List

from as64.plugins.metadata import PluginMetaData


class PluginValidationError(Exception):
    """Custom exception for plugin validation errors."""
    pass


class BasePlugin(ABC):
    metadata: PluginMetaData = None
    
    def __init__(self):
        pass

    def is_valid(self) -> bool:
        """
        Validate the plugin.
        
        [Lifecycle Function] This is automatically called before use
        
        [Use] Override if validation logic is needed, returning False will cause an error to fire.
              May raise a PluginValidationError exception to provide the user a detailed message.
        """
        return True
    
    
class Plugin(BasePlugin):
    def initialize(self):
        """
        Initialize the plugin.
        
        [Lifecycle Function] This is automatically called after ALL plugins have been instantiated
        
        [Use] Override if initialization logic is needed, or if this plugin depends on another plugin having been loaded.
        """
        pass
    
    def start(self, game, controller):
        """
        Start the plugin.
        
        [Lifecycle Function] This is automatically called when the AS64 processing loop is started 
        
        [Use] Override if start logic is needed.
        """
        pass
    
    def stop(self):
        """
        Stop the plugin.
        
        [Lifecycle Function] This is automatically called when the AS64 processing loop is stopped 
        
        [Use] Override if stop logic is needed.
        """
        pass
    
    def shutdown(self):
        """
        Shutdown the plugin.
        
        [Lifecycle Function] This is automatically called when AS64 is closed
        
        [Use] Override if shutdown logic is needed.
        """
        pass
    
    @property
    def is_realtime(self) -> bool:
        return callable(getattr(self, "execute", None))
    
    # def execute(self, *args, **kwargs):
    #     """
    #     Execute logic on each frame
    #     """
    #     pass
    
    

class GameStatePlugin(Plugin):
    pass


class SplitPlugin(BasePlugin):
    @abstractmethod
    def split(self):
        pass
    
    @abstractmethod
    def skip(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def index(self):
        pass
    
    @abstractmethod
    def sync(self):
        pass


class CapturePlugin(BasePlugin):
    @abstractmethod
    def capture(self):
        """
        Capture functionality
        """
        pass

    @abstractmethod
    def get_available_sources(self) -> List[str]:
        pass