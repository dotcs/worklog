import logging
import sys
import argparse
import os
from datetime import datetime, timezone, timedelta

LOG_FORMAT = logging.BASIC_FORMAT
LOG_LEVELS = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

CONFIG_FILES = [
    os.path.expanduser("~/.config/worklog/config"),
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.cfg"),
]
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


def get_logger() -> logging.Logger:
    logger = logging.getLogger("worklog")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def _format_timedelta(td: timedelta) -> str:
    try:
        total_secs = td.total_seconds()
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    except ValueError:
        return "{:02}:{:02}:{:02}".format(0, 0, 0)


def _positive_int(value: str) -> int:
    value_int = int(value)
    if value_int <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive int value.")
    return value_int


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("WorkLog")
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    subparsers = parser.add_subparsers(dest="subcmd")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument(
        "type",
        choices=["start", "stop", "undo"],
        help="Commits a new entry to the log.",
    )
    commit_parser.add_argument(
        "--offset-minutes",
        type=float,
        default=0,
        help="Offset of the start/stop time in minutes",
    )

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument(
        "--yesterday",
        action="store_true",
        help="Returns the status of yesterday instead of today.",
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
        help="Defines many log entries should be shown. System pager will be used if n > 20.",
    )
    log_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show all entries. System pager will be used.",
    )

    return parser
