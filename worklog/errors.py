from enum import Enum


class ErrMsg(Enum):
    MISSING_SESSION_ENTRY = (
        "At least one session has a missing {type} entry on date {date}"
    )
    MISSING_TASK_ENTRY = "Task '{task_id}' is missing a {type} entry on date {date}"
    WRONG_TASK_ORDER = (
        "Task '{task_id}' has been closed before it has been stared on date {date}"
    )
