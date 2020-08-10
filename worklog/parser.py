from typing import List
from datetime import datetime, timezone, timedelta
import re
import argparse

_help_time_arg = (
    "Exact point in time. "
    "Can be a either hours and minutes (format: 'hh:mm') on the same day or a full ISO "
    "format string, such as '2020-08-05T08:15:00+02:00'. "
    "In the latter case the local timezone is used if no timezone is specified "
    "explicitly."
)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        "Worklog", description="Simple CLI tool to log work and projects."
    )
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    subparsers = parser.add_subparsers(dest="subcmd")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument(
        "type", choices=["start", "stop"], help="Commits a new entry to the log.",
    )
    _add_timeshift_args(commit_parser)
    commit_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force command, will auto-stop running tasks",
    )

    task_parser = subparsers.add_parser("task")
    task_parser.add_argument(
        "type",
        choices=["start", "stop", "list", "report"],
        help="Starts/stops or list tasks",
    )
    task_parser.add_argument(
        "--id", type=str, help="Task identifier",
    )
    task_parser.add_argument(
        "--auto-close",
        action="store_true",
        help=(
            "Auto closes open tasks. "
            "This flag is only relevant if type is set to 'start'."
        ),
    )
    _add_timeshift_args(task_parser)

    status_parser = subparsers.add_parser("status")
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

    doctor_parser = subparsers.add_parser("doctor")

    log_parser = subparsers.add_parser("log")
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
        "--category", choices=["session", "task"], help="Filter category",
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

    now = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
    current_month: str = now.isoformat()[: len("2000-01")]
    next_month: str = (now.replace(day=1) + timedelta(days=31)).isoformat()[
        : len("2000-01")
    ]

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument(
        "--month-from",
        type=_year_month_parser,
        default=current_month,
        help=(
            "Month from which the aggregation should be started (inclusive). "
            "By default the current calendar month is selected."
        ),
    )
    report_parser.add_argument(
        "--month-to",
        type=_year_month_parser,
        default=next_month,
        help=(
            "Month to which the aggregation should be started (exclusive). "
            "By default the next calendar month is selected."
        ),
    )

    return parser


def _year_month_parser(value: str) -> datetime:
    local_tz = datetime.utcnow().astimezone().tzinfo
    if not re.match("\d{4}\-\d{2}", value):
        raise argparse.ArgumentTypeError(f"{value} is not in the format YYYY-MM")
    year, month = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=1, tzinfo=local_tz)


def _year_month_day_parser(value: str) -> datetime:
    local_tz = datetime.utcnow().astimezone().tzinfo
    if not re.match("\d{4}\-\d{2}\-\d{2}", value):
        raise argparse.ArgumentTypeError(f"{value} is not in the format YYYY-MM-DD")
    year, month, day = [int(x) for x in value.split("-")]
    return datetime(year=year, month=month, day=day, tzinfo=local_tz)


def _positive_int(value: str) -> int:
    value_int = int(value)
    if value_int <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive int value.")
    return value_int


def _add_timeshift_args(parser: argparse.ArgumentParser):
    timeshift_grp = parser.add_mutually_exclusive_group()
    timeshift_grp.add_argument(
        "--offset-minutes",
        type=float,
        default=0,
        help=(
            "Offset of the start/stop time in minutes. "
            "Positive values shift the timestamp into the future, negative "
            "values shift it into the past."
        ),
    )
    timeshift_grp.add_argument("--time", help=_help_time_arg)

