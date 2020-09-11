from configparser import ConfigParser
from argparse import ArgumentParser, Namespace
from datetime import date, timedelta
import json

import worklog.constants as wc
from worklog.log import Log
from worklog.utils.time import calc_log_time


def dispatch(
    log: Log, parser: ArgumentParser, cli_args: Namespace, cfg: ConfigParser
) -> None:
    """
    Dispatch request to Log instance based on CLI arguments and
    configuration values.
    """
    if cli_args.subcmd == wc.SUBCMD_SESSION:
        if cli_args.type in [wc.TOKEN_START, wc.TOKEN_STOP]:
            log.commit(
                wc.TOKEN_SESSION,
                cli_args.type,
                cli_args.offset_minutes,
                cli_args.time,
                force=cli_args.force,
            )
    elif cli_args.subcmd == wc.SUBCMD_TASK:
        if cli_args.type in [wc.TOKEN_START, wc.TOKEN_STOP]:
            if cli_args.type == wc.TOKEN_START and cli_args.auto_stop:
                commit_dt = calc_log_time(cli_args.offset_minutes, cli_args.time)
                log.stop_active_tasks(commit_dt)
            log.commit(
                wc.TOKEN_TASK,
                cli_args.type,
                cli_args.offset_minutes,
                cli_args.time,
                identifier=cli_args.id,
            )
        elif cli_args.type == "list":
            log.list_tasks()
        elif cli_args.type == "report":
            log.task_report(cli_args.id)
    elif cli_args.subcmd == wc.SUBCMD_STATUS:
        hours_target = float(cfg.get("workday", "hours_target"))
        hours_max = float(cfg.get("workday", "hours_max"))
        fmt = cli_args.fmt
        query_date = date.today()
        if cli_args.yesterday:
            query_date -= timedelta(days=1)
        elif cli_args.date:
            query_date = cli_args.date.date()
        log.status(hours_target, hours_max, query_date=query_date, fmt=fmt)
    elif cli_args.subcmd == wc.SUBCMD_DOCTOR:
        log.doctor()
    elif cli_args.subcmd == wc.SUBCMD_LOG:
        n = cli_args.number
        no_pager_max_entries = int(cfg.get("worklog", "no_pager_max_entries"))
        use_pager = not cli_args.no_pager and (cli_args.all or n > no_pager_max_entries)
        categories = cli_args.category
        if not cli_args.all:
            log.log(cli_args.number, use_pager, categories)
        else:
            log.log(-1, use_pager, categories)
    elif cli_args.subcmd == wc.SUBCMD_REPORT:
        log.report(cli_args.date_from, cli_args.date_to)
