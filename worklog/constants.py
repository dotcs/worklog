from typing import List, Optional
import logging
import os
from datetime import datetime, timezone, tzinfo

LOG_FORMAT: str = logging.BASIC_FORMAT
LOG_LEVELS: List[int] = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

CONFIG_FILES: List[str] = [
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.cfg"),
    os.path.expanduser("~/.config/worklog/config"),
]

LOCAL_TIMEZONE: Optional[tzinfo] = datetime.now(timezone.utc).astimezone().tzinfo

DEFAULT_LOGGER_NAME = "worklog"

CATEGORY_SESSION = "session"
CATEGORY_TASK = "task"
