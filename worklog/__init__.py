import os
from configparser import ConfigParser
from argparse import ArgumentParser, Namespace
from datetime import date, timedelta
from io import StringIO

from worklog.parser import get_arg_parser
from worklog.utils import (
    configure_logger,
    LOG_LEVELS,
    CONFIG_FILES,
    calc_log_time,
)
from worklog.log import Log


def dispatch(
    log: Log, parser: ArgumentParser, cli_args: Namespace, cfg: ConfigParser
) -> None:
    """
    Dispatch request to Log instance based on CLI arguments and
    configuration values.
    """
    if cli_args.subcmd == "commit":
        if cli_args.type in ["start", "stop"]:
            log.commit(
                "session",
                cli_args.type,
                cli_args.offset_minutes,
                cli_args.time,
                force=cli_args.force,
            )
    elif cli_args.subcmd == "task":
        if cli_args.auto_close == True and cli_args.type != "start":
            raise parser.error(
                '--auto-close is only allowed if the type is set to "start"',
            )
        if cli_args.type in ["start", "stop"]:
            if cli_args.id is None:
                raise parser.error(
                    "--id is required when a new task is started/stopped"
                )
            if cli_args.type == "start" and cli_args.auto_close:
                commit_dt = calc_log_time(cli_args.offset_minutes, cli_args.time)
                log.stop_active_tasks(commit_dt)
            log.commit(
                "task",
                cli_args.type,
                cli_args.offset_minutes,
                cli_args.time,
                identifier=cli_args.id,
            )
        elif cli_args.type == "list":
            log.list_tasks()
        elif cli_args.type == "report":
            if cli_args.id is None:
                raise parser.error("--id is required when requesting a report")
            log.task_report(cli_args.id)
    elif cli_args.subcmd == "status":
        hours_target = float(cfg.get("workday", "hours_target"))
        hours_max = float(cfg.get("workday", "hours_max"))
        fmt = cli_args.fmt
        query_date = date.today()
        if cli_args.yesterday:
            query_date -= timedelta(days=1)
        elif cli_args.date:
            query_date = cli_args.date.date()
        log.status(hours_target, hours_max, query_date=query_date, fmt=fmt)
    elif cli_args.subcmd == "doctor":
        log.doctor()
    elif cli_args.subcmd == "log":
        n = cli_args.number
        no_pager_max_entries = int(cfg.get("worklog", "no_pager_max_entries"))
        use_pager = not cli_args.no_pager and (cli_args.all or n > no_pager_max_entries)
        categories = cli_args.category
        if not cli_args.all:
            log.log(cli_args.number, use_pager, categories)
        else:
            log.log(-1, use_pager, categories)
    elif cli_args.subcmd == "report":
        log.report(cli_args.month_from, cli_args.month_to)


def run() -> None:
    """ Main method """
    logger = configure_logger()
    parser = get_arg_parser()

    cli_args = parser.parse_args()
    log_level = LOG_LEVELS[min(cli_args.verbosity, len(LOG_LEVELS) - 1)]
    logger.setLevel(log_level)

    logger.debug(f"Parsed CLI arguments: {cli_args}")
    logger.debug(f"Path to config files: {CONFIG_FILES}")

    if cli_args.subcmd is None:
        parser.print_help()
        return

    cfg = ConfigParser()
    cfg.read(CONFIG_FILES)

    with StringIO() as ss:
        cfg.write(ss)
        ss.seek(0)
        logger.debug(f"Config content:\n{ss.read()}\nEOF")

    worklog_fp = os.path.expanduser(cfg.get("worklog", "path"))
    log = Log(worklog_fp)

    dispatch(log, parser, cli_args, cfg)


if __name__ == "__main__":
    run()
