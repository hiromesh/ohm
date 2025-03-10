#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import ohm

CONFIG_ROOT = Path.home() / ".ohm"

def get_package_root():
    package_root = Path(ohm.__file__).parent.parent
    return package_root

OHM_ROOT = get_package_root()
DEFAULT_WORKSPACE_ROOT = OHM_ROOT / "workspace"

EXAMPLE_PATH = OHM_ROOT / "examples"


TMP = OHM_ROOT / "tmp"

SOURCE_ROOT = OHM_ROOT / "ohm"
PROMPT_PATH = SOURCE_ROOT / "prompts"
TEMPLATE_FOLDER_PATH = OHM_ROOT / "template"

MEM_TTL = 24 * 30 * 3600

MESSAGE_ROUTE_FROM = "from"
MESSAGE_ROUTE_TO = "to"
MESSAGE_ROUTE_CAUSE_BY = "cause"
MESSAGE_META_ROLE = "role"
MESSAGE_ROUTE_TO_ALL = "<all>"
MESSAGE_ROUTE_TO_NONE = "<none>"
MESSAGE_ROUTE_TO_SELF = "<self>"
