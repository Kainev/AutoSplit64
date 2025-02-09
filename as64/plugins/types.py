# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from typing import (
    Type,
    Optional
)

from .base import (
    BasePlugin,
    PluginMetaData
)

class DiscoveredPlugin:
    def __init__(self, cls: Type[BasePlugin]):
        self.cls = cls

        if hasattr(cls, 'metadata') and isinstance(cls.metadata, PluginMetaData):
            self.name = cls.metadata.name
            self.version = cls.metadata.version
            self.dependencies = cls.metadata.required_plugins
        else:
            fallback_name = cls.__name__
            self.name = fallback_name
            self.version = "0.0.0"
            self.dependencies = []
            cls.metadata = PluginMetaData(name=fallback_name, version="0.0.0")
        
        try:
            self.category: Optional[Type[BasePlugin]] = cls.__mro__[1]
        except IndexError:
            self.category: Optional[Type[BasePlugin]] = None
