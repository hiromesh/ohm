#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/4/29 15:35
@Author  : alexanderwu
@File    : __init__.py
"""

from ohm.tools import libs  # this registers all tools
from ohm.tools.tool_registry import TOOL_REGISTRY
from ohm.configs.search_config import SearchEngineType
from ohm.configs.browser_config import WebBrowserEngineType


_ = libs, TOOL_REGISTRY  # Avoid pre-commit error


class SearchInterface:
    async def asearch(self, *args, **kwargs):
        ...


__all__ = ["SearchEngineType", "WebBrowserEngineType", "TOOL_REGISTRY"]
