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

SUBCMD_SESSION = "session"
SUBCMD_DOCTOR = "doctor"
SUBCMD_TASK = "task"
SUBCMD_STATUS = "status"
SUBCMD_LOG = "log"
SUBCMD_REPORT = "report"

COL_COMMIT_DATETIME = "commit_dt"
COL_LOG_DATETIME = "log_dt"
COL_CATEGORY = "category"
COL_TYPE = "type"
COL_TASK_IDENTIFIER = "identifier"

TOKEN_START = "start"
TOKEN_STOP = "stop"
TOKEN_SESSION = "session"
TOKEN_TASK = "task"

