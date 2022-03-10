import os
from configparser import ConfigParser
from io import StringIO
import json
from typing import Tuple, Optional
import typer
from datetime import datetime

from worklog.breaks import AutoBreak
import worklog.constants as wc
from worklog.log import Log
from worklog.parser import get_arg_parser
from worklog.utils.time import calc_log_time
from worklog.utils.logger import configure_logger
from worklog.dispatcher import dispatch


def configure_worklog() -> Tuple[Log, ConfigParser]:
    """ Main method """
    logger = configure_logger()

    # log_level = wc.LOG_LEVELS[min(cli_args.verbosity, len(wc.LOG_LEVELS) - 1)]
    # logger.setLevel(log_level)

    # logger.debug(f"Parsed CLI arguments: {cli_args}")
    # logger.debug(f"Path to config files: {wc.CONFIG_FILES}")

    # if cli_args.subcmd is None:
    #     parser.print_help()
    #     return

    cfg = ConfigParser()
    cfg.read(wc.CONFIG_FILES)

    with StringIO() as ss:
        cfg.write(ss)
        ss.seek(0)
        logger.debug(f"Config content:\n{ss.read()}\nEOF")

    worklog_fp = os.path.expanduser(cfg.get("worklog", "path"))
    log = Log(worklog_fp)

    limits = json.loads(cfg.get("workday", "auto_break_limit_minutes"))
    durations = json.loads(cfg.get("workday", "auto_break_duration_minutes"))
    log.auto_break = AutoBreak(limits, durations)

    return log, cfg


# Taken from https://github.com/tiangolo/typer/issues/140#issuecomment-898937671
def MutuallyExclusiveGroup(size=2):
    group = set()

    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in group:
            group.add(param.name)
        if len(group) > size - 1:
            raise typer.BadParameter(
                f"{param.name} is mutually exclusive with {group.pop()}"
            )
        return value

    return callback


timeshift_grp = MutuallyExclusiveGroup()
offset_minutes_opt: Optional[int] = typer.Option(
    None,
    "--offset-minutes",
    "-om",
    callback=timeshift_grp,
    help=(
        "Offset of the start/stop time in minutes. "
        "Positive values shift the timestamp into the future, negative "
        "values shift it into the past."
    ),
)
time_opt: Optional[str] = typer.Option(
    None,
    callback=timeshift_grp,
    help=(
        "Exact point in time. "
        "Can be a either hours and minutes (format: 'hh:mm') on the same day or a full ISO "
        "format string, such as '2020-08-05T08:15:00+02:00'. "
        "In the latter case the local timezone is used if the timezone part is left empty."
    ),
)
