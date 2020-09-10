from enum import Enum


class ErrMsg(Enum):
    MISSING_SESSION_ENTRY = (
        "At least one session has a missing {type} entry on date {date}"
    )
    MISSING_TASK_ENTRY = "Task '{task_id}' is missing a {type} entry on date {date}"
    WRONG_SESSION_ORDER = (
        "Wrong order of session entries on date {date}. "
        "This happens either if a session has been stopped before it has been "
        "started or if two or more sessions have been started or stopped at "
        "the same time."
    )
    WRONG_TASK_ORDER = (
        "Wrong order of task entries for task '{task_id}' on date {date}. "
        "This happens either if a task has been stopped before it has been "
        "started or if the same task has been started or stopped at twice."
    )
