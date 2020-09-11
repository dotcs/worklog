from typing import List
from datetime import datetime, timezone, timedelta
import re
import argparse

import worklog.constants as wc

_help_time_arg = (
    "Exact point in time. "
    "Can be a either hours and minutes (format: 'hh:mm') on the same day or a full ISO "
    "format string, such as '2020-08-05T08:15:00+02:00'. "
    "In the latter case the local timezone is used if the timezone part is left empty."
)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        "Worklog", description="Simple CLI tool to log work and projects."
    )
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    subparsers = parser.add_subparsers(dest="subcmd")

    _add_session_parser(subparsers)
    _add_task_parser(subparsers)
    _add_status_parser(subparsers)
    _add_doctor_parser(subparsers)
    _add_log_parser(subparsers)
    _add_report_parser(subparsers)

    return parser


def _add_session_parser(subparsers: argparse._SubParsersAction):
    session_parser = subparsers.add_parser(
        wc.SUBCMD_SESSION,
        description=(
            "Commit the start or end of a new working session to the worklog file. "
            "Use this function to stamp in the morning and stamp out in the evening."
        ),
    )
    session_parser.add_argument(
        "type",
        choices=[wc.TOKEN_START, wc.TOKEN_STOP],
        help="Persists a new work session or closes a work session.",
    )
    _add_timeshift_args(session_parser)
    session_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force command, will auto-stop running tasks.",
    )


def _add_task_parser(subparsers: argparse._SubParsersAction):
    task_parser = subparsers.add_parser(
        wc.SUBCMD_TASK,
        description=(
            "Tasks are pieces of work to be done or undertaken. "
            "A task can only be started during an ongoing session. "
            "Use 'wl session start' to start a new working session."
        ),
    )
    task_parser_type = task_parser.add_subparsers(dest="type")

    # task start
    task_start_parser = task_parser_type.add_parser(wc.TOKEN_START)
    task_start_parser.add_argument(
        "id", type=str, help="Task identifier, can be freely chosen",
    )
    task_start_parser.add_argument(
        "-as",
        "--auto-stop",
        action="store_true",
        help=("Automatically stops open tasks."),
    )
    _add_timeshift_args(task_start_parser)

    # task stop
    task_stop_parser = task_parser_type.add_parser(wc.TOKEN_STOP)
    task_stop_parser.add_argument(
        "id", type=str, help="Task identifier of a running task.",
    )
    _add_timeshift_args(task_stop_parser)

    # task list
    task_list_parser = task_parser_type.add_parser("list")

    # task report
    task_report_parser = task_parser_type.add_parser("report")
    task_report_parser.add_argument(
        "id", type=str, help="Task identifier of a recorded task.",
    )


def _add_status_parser(subparsers: argparse._SubParsersAction):
    status_parser = subparsers.add_parser(
        wc.SUBCMD_STATUS,
        description=(
            "The status commend shows the tracking results for an individual day. "
            "By default the current day is selected. "
            "For integration of the current status into a status bar, use the `--fmt` "
            "argument."
        ),
    )
    status_time_grp = status_parser.add_mutually_exclusive_group()
    status_time_grp.add_argument(
        "--yesterday",
        action="store_true",
        help="Returns the status of yesterday instead of today.",
    )
    status_time_grp.add_argument(
        "--date", type=_year_month_day_parser, help=("Date in the form YYYY-MM-DD")
    )
    status_parser.add_argument(
        "--fmt", type=str, default=None, help="Use a custom formatted string"
    )


def _add_doctor_parser(subparsers: argparse._SubParsersAction):
    doctor_parser = subparsers.add_parser(
        wc.SUBCMD_DOCTOR,
        description=(
            "The doctor command checks the worklog for missing or problematic entries. "
            "It will report the following issues: non-closed working sessions"
        ),
    )


def _add_log_parser(subparsers: argparse._SubParsersAction):
    log_parser = subparsers.add_parser(
        wc.SUBCMD_LOG,
        description=(
            "Shows the content of the worklog file sorted after the date and time of the "
            "entry. "
            "Use this command to manually review the content of the worklog."
        ),
    )
    log_parser.add_argument(
        "-n",
        "--number",
        type=_positive_int,
        default=10,
        help=(
            "Defines many log entries should be shown. "
            "System pager will be used if n > 20."
        ),
    )
    log_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all entries. System pager will be used.",
    )
    log_parser.add_argument(
        "--category", choices=[wc.TOKEN_SESSION, wc.TOKEN_TASK], help="Filter category",
    )
    log_parser.add_argument(
        "--no-pager",
        action="store_true",
        help=(
            "Don't use a the system pager. "
            "Prints all output to STDOUT regardless of how many entries will be shown. "
            "This flag should be used if there are problems with the system pager."
        ),
    )


def _add_report_parser(subparsers: argparse._SubParsersAction):
    now = (
        datetime.now(timezone.utc)
        .astimezone(tz=wc.LOCAL_TIMEZONE)
        .replace(microsecond=0)
    )
    current_month: str = now.replace(day=1).isoformat()[: len("2000-01-01")]
    next_month: str = (now.replace(day=1) + timedelta(days=31)).replace(
        day=1
    ).isoformat()[: len("2000-01-01")]

    report_parser = subparsers.add_parser(
        wc.SUBCMD_REPORT,
        description=(
            "Creates a report for a given time window. "
            "Working time will be aggregated on a monthly, weekly and daily basis. "
            "Tasks will be aggregated separately. "
            "By default the current month will be used for the report."
        ),
    )
    report_parser.add_argument(
        "--date-from",
        type=_combined_month_or_day_or_week_parser,
        default=current_month,
        help=(
            "Date from which the aggregation should be started (inclusive). "
            "By default the start of the current calendar month is selected. "
            "Allowed input formats are YYYY-MM-DD, YYYY-MM and YYYY-WXX, with "
            "XX referring to the week number, e.g. 35."
        ),
    )
    report_parser.add_argument(
        "--date-to",
        type=_combined_month_or_day_or_week_parser,
        default=next_month,
        help=(
            "Date to which the aggregation should be started (exclusive). "
            "By default the next calendar month is selected. "
            "Allowed input formats are YYYY-MM-DD, YYYY-MM and YYYY-WXX, with "
            "XX referring to the week number, e.g. 35."
        ),
    )


def _combined_month_or_day_or_week_parser(value: str) -> datetime:
    if re.match(r"^\d{4}\-\d{2}$", value):
        return _year_month_parser(value)
    elif re.match(r"^\d{4}\-\d{2}\-\d{2}$", value):
        return _year_month_day_parser(value)
    elif re.match(r"^\d{4}-W\d{2}$", value):
        return _calendar_week_parser(value)
    raise argparse.ArgumentTypeError(f"{value} is not a valid format")


def _year_month_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}\-\d{2}$", value):
        raise argparse.ArgumentTypeError(f"{value} is not in the format YYYY-MM")
    year, month = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=1, tzinfo=wc.LOCAL_TIMEZONE)


def _year_month_day_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}\-\d{2}\-\d{2}$", value):
        raise argparse.ArgumentTypeError(f"{value} is not in the format YYYY-MM-DD")
    year, month, day = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=day, tzinfo=wc.LOCAL_TIMEZONE)


def _calendar_week_parser(value: str) -> datetime:
    if not re.match(r"^\d{4}-W\d{2}$", value):
        raise argparse.ArgumentTypeError(f"{value} is not in the format cwWW")
    dt = datetime.strptime(value + "-1", "%Y-W%W-%w").replace(tzinfo=wc.LOCAL_TIMEZONE)
    return dt


def _positive_int(value: str) -> int:
    value_int = int(value)
    if value_int <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive int value.")
    return value_int


def _add_timeshift_args(parser: argparse.ArgumentParser):
    timeshift_grp = parser.add_mutually_exclusive_group()
    timeshift_grp.add_argument(
        "-om",
        "--offset-minutes",
        type=float,
        default=0,
        help=(
            "Offset of the start/stop time in minutes. "
            "Positive values shift the timestamp into the future, negative "
            "values shift it into the past."
        ),
    )
    timeshift_grp.add_argument("-t", "--time", help=_help_time_arg)

