from __future__ import annotations

import asyncio
import inspect
import sys
from contextvars import ContextVar
from datetime import datetime
from functools import partial
from typing import Any

from loguru import logger as _logger

from ohm.constants import OHM_ROOT
from dataclasses import dataclass

LLM_STREAM_QUEUE: ContextVar[asyncio.Queue] = ContextVar("llm-stream")

@dataclass
class ToolLogItem:
    type: str =""
    name: str
    value: Any


TOOL_LOG_END_MARKER = ToolLogItem(
    type="str", name="end_marker", value="\x18\x19\x1B\x18"
) 

_print_level = "INFO"


def define_log_level(print_level="INFO",
                     logfile_level="DEBUG",
                     name: str = None):
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = f"{name}_{formatted_date}" if name else formatted_date 

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(OHM_ROOT / f"logs/{log_name}.txt", level=logfile_level)
    return _logger


logger = define_log_level()


def log_llm_stream(msg):
    queue = get_llm_stream_queue()
    if queue:
        queue.put_nowait(msg)
    _llm_stream_log(msg)


async def get_human_input(prompt: str = ""):
    if inspect.iscoroutinefunction(_get_human_input):
        return await _get_human_input(prompt)
    else:
        return _get_human_input(prompt)


def set_llm_stream_logfunc(func):
    global _llm_stream_log
    _llm_stream_log = func


def set_human_input_func(func):
    global _get_human_input
    _get_human_input = func


_llm_stream_log = partial(print, end="")

_tool_output_log = (
    lambda *args, **kwargs: None
) 

def create_llm_stream_queue():
    queue = asyncio.Queue()
    LLM_STREAM_QUEUE.set(queue)
    return queue


def get_llm_stream_queue():
    return LLM_STREAM_QUEUE.get(None)


_get_human_input = input


def _llm_stream_log(msg):
    if _print_level in ["INFO"]:
        print(msg, end="")
