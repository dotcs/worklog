from enum import Enum


class ErrMsg(Enum):
    NA = "N/A"
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
    EMPTY_LOG_DATA = (
        "Fatal: No log data available. "
        "Start a new log entry with 'wl session start'."
    )
    EMPTY_LOG_DATA_FOR_DATE = "No log data available for {query_date}."
    STOP_SESSION_TASKS_RUNNING = (
        "Fatal. Cannot stop, because tasks are still running. "
        "Stop running tasks first: {active_tasks:} or use --force flag."
    )
