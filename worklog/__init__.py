import os
from configparser import ConfigParser
from io import StringIO
import json
import pkg_resources

from worklog.breaks import AutoBreak
import worklog.constants as wc
from worklog.log import Log
from worklog.parser import get_arg_parser
from worklog.utils.time import calc_log_time
from worklog.utils.logger import configure_logger
from worklog.dispatcher import dispatch


try:
    __version__ = pkg_resources.get_distribution("dcs-" + __name__).version
except Exception:
    __version__ = "unknown"


def run() -> None:
    """ Main method """
    logger = configure_logger()
    parser = get_arg_parser()

    cli_args = parser.parse_args()
    log_level = wc.LOG_LEVELS[min(cli_args.verbosity, len(wc.LOG_LEVELS) - 1)]
    logger.setLevel(log_level)

    logger.debug(f"Parsed CLI arguments: {cli_args}")
    logger.debug(f"Path to config files: {wc.CONFIG_FILES}")

    if cli_args.subcmd is None:
        parser.print_help()
        return

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

    dispatch(log, parser, cli_args, cfg)


if __name__ == "__main__":
    run()
