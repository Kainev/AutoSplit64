# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license


import asyncio
import logging
from functools import wraps

import asyncio

logger = logging.getLogger("RPC")

_RPC_REGISTRY = {}

def register(name=None, processor=None):
    """
    Decorator to register a function as an RPC call.
    Usage:
        @rpc("someName", processor=func)
        def some_func(*args, **kwargs):
            ...
    """
    def decorator(func):
        proc_name = name or func.__name__
        _RPC_REGISTRY[proc_name] = (func, processor)

        return func
    return decorator

def get(proc_name):
    """Retrieve a registered RPC function by name, or None if not found"""
    return _RPC_REGISTRY.get(proc_name)


async def call(proc_name, args=None, kwargs=None):
    """
    Dispatches the RPC call to a registered function (sync or async)
    Returns (result, error)
    """
    args = args or []
    kwargs = kwargs or {}
    entry = get(proc_name)
    
    if not entry:
        return None, f"Unknown RPC '{proc_name}'"
    
    func, processor = entry

    try:
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
            
        if processor:
            result = processor(result)
            
        return result, None
    except Exception as ex:
        return None, str(ex)