from datetime import datetime, timedelta, timezone
import logging
import configparser
import pathlib
import os
import sys
import argparse
import numpy as np
import pandas as pd
import subprocess
import tempfile

logger = logging.getLogger(__name__)

LOG_FORMAT = logging.BASIC_FORMAT
LOG_LEVELS = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
CONFIG_FILES = [
    os.path.expanduser("~/.config/worklog/config"),
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.cfg"),
]
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


class Log(object):
    _log_fp = None
    _log_df = None
    _separator = None

    def __init__(self, fp, separator="|"):
        self._log_fp = fp
        self._separator = separator

        self._create_file_if_not_exists()
        self._read()

    def _create_file_if_not_exists(self):
        if not os.path.exists(self._log_fp):
            # create empty file if it does not exist
            with open(self._log_fp, "w") as fh:
                fh.write("")

    def _read(self):
        try:
            self._log_df = pd.read_csv(
                self._log_fp, sep=self._separator, parse_dates=["datetime"]
            )
        except pd.errors.EmptyDataError:
            self._log_df = pd.DataFrame([], columns=["datetime", "category", "type"],)

        self._log_df["date"] = self._log_df["datetime"].apply(lambda x: x.date)
        self._log_df["time"] = self._log_df["datetime"].apply(lambda x: x.time)

    def _persist(self, df, reload=False):
        persisted_fields = ["datetime", "category", "type"]
        df[persisted_fields].to_csv(self._log_fp, sep=self._separator, index=False)
        if reload:
            self._read()

    def commit(self, type_, offset_min):
        if type_ not in ["start", "stop"]:
            raise ValueError(f'Type must be one of {", ".join(type_)}')

        commit_date = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        commit_date += timedelta(minutes=offset_min)

        new_entry = pd.DataFrame(
            {
                "datetime": pd.to_datetime(commit_date),
                "category": "start_stop",
                "type": type_,
            },
            index=[0],
        )
        df = pd.concat((self._log_df, new_entry))
        self._persist(df, reload=True)

    def doctor(self):
        def test_alternating_start_stop(group):
            last_type = None
            for i, row in group.where(group["category"] == "start_stop").iterrows():
                if i == 0 and row["type"] != "start":
                    logger.error(
                        f'First entry of type "start_stop" on date {row.date} is not "start".'
                    )
                if row["type"] == last_type:
                    logger.error(
                        f'"start_stop" entries on date {row.date} are not ordered correctly.'
                    )
                last_type = row["type"]
            if last_type != "stop":
                logger.error(f"Date {row.date} has no stop entry.")

        self._log_df.groupby("date").apply(test_alternating_start_stop)

    def status(self, hours_target, hours_max, date="today", fmt=None):
        if self._log_df.shape[0] == 0:
            sys.stdout.write("No data available\n")
            return

        query_date = datetime.now().date()
        if date == "yesterday":
            query_date -= timedelta(days=1)

        sub_df = self._log_df[self._log_df.date == query_date]
        sub_df = sub_df[["datetime", "type"]]

        is_curr_working = (
            sub_df.iloc[-1]["type"] == "start" if sub_df.shape[0] > 0 else False
        )
        logger.debug(f"Currently working: {is_curr_working}")

        if is_curr_working:
            target_date = sub_df.iloc[0].datetime.date()
            fill_ts = min(
                datetime.now(timezone.utc).astimezone().replace(microsecond=0),
                datetime(
                    target_date.year,
                    target_date.month,
                    target_date.day,
                    23,
                    59,
                    59,
                    0,
                    LOCAL_TIMEZONE,
                ).astimezone(),
            )
            # attach another row with the current time
            help_df = pd.DataFrame(
                {"datetime": pd.to_datetime(fill_ts.isoformat()), "type": "stop"},
                index=[0],
            )
            sub_df = pd.concat((sub_df, help_df))
            logger.warning(f"Fill missing stop value with {fill_ts}")
        sub_df["datetime_shift"] = sub_df["datetime"].shift(1)
        x = sub_df[sub_df["type"] == "stop"]
        total_time = (x["datetime"] - x["datetime_shift"]).sum()
        total_time_str = _format_timedelta(total_time)

        hours_target_dt = timedelta(hours=hours_target)
        hours_max_dt = timedelta(hours=hours_max)

        now = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        end_time = now + (hours_target_dt - total_time)
        end_time_str = end_time.strftime("%H:%M:%S")
        remaining_time_str = _format_timedelta(end_time - now)

        percentage = round(
            total_time.total_seconds() / hours_target_dt.total_seconds() * 100
        )

        lines = [
            ("Status", "Tracking on" if is_curr_working else "Tracking off"),
            ("Total time today", f"{total_time_str} ({percentage}%)"),
            ("Remaining time today", f"{remaining_time_str} ({100 - percentage}%)"),
        ]
        if is_curr_working and date == "today":
            lines += [("End of work", end_time_str,)]

        key_max_len = max([len(line[0]) for line in lines])
        fmt_string = "{:" + str(key_max_len + 1) + "s}: {}"

        val = "\n".join(fmt_string.format(*line) for line in lines)

        if fmt is None:
            sys.stdout.write(val + "\n")
        else:
            sys.stdout.write(
                fmt.format(
                    status="on" if is_curr_working else "off",
                    percentage=percentage,
                    end_of_work=end_time_str,
                    total_time=total_time_str,
                    remaining_time=remaining_time_str,
                )
            )

    def log(self, n, use_pager):
        if self._log_df.shape[0] == 0:
            sys.stdout.write("No data available\n")
            return

        fields = ["date", "time", "category", "type"]
        df = self._log_df[fields].iloc[::-1]
        if n > 0:
            df = df.tail(n=n)
        if not use_pager:
            sys.stdout.write(df.to_string(index=False) + "\n")
        else:
            fh = tempfile.NamedTemporaryFile(mode="w")
            fh.write(df.to_string(index=False))
            fh.flush()
            pager = os.getenv("PAGER", "less")
            process = subprocess.Popen([pager, fh.name])
            process.wait()
            fh.close()


def _format_timedelta(td):
    total_secs = td.total_seconds()
    hours, remainder = divmod(total_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))


def dispatch(cfg, cli_args):
    worklog_fp = os.path.expanduser(cfg.get("worklog", "path"))

    log = Log(worklog_fp)

    if cli_args.subcmd == "commit":
        if cli_args.type in ["start", "stop"]:
            log.commit(cli_args.type, cli_args.offset_minutes)
        elif cli_args.type == "undo":
            # entries = WorkLogEntries()
            # entries.parse(worklog_fp)
            # entries.undo()
            # entries.persist(worklog_fp, mode='overwrite')
            pass
    elif cli_args.subcmd == "status":
        hours_target = float(cfg.get("workday", "hours_target"))
        hours_max = float(cfg.get("workday", "hours_max"))
        fmt = cli_args.fmt
        if cli_args.yesterday:
            log.status(hours_target, hours_max, date="yesterday", fmt=fmt)
        else:
            log.status(hours_target, hours_max, fmt=fmt)
    elif cli_args.subcmd == "doctor":
        log.doctor()
    elif cli_args.subcmd == "log":
        n = cli_args.number
        use_pager = cli_args.all or n > 20
        log.log(cli_args.number, use_pager)


def _positive_int(value):
    value_int = int(value)
    if value_int <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive int value.")
    return value_int


def run():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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

    cli_args = parser.parse_args()

    logger.setLevel(LOG_LEVELS[min(cli_args.verbosity, len(LOG_LEVELS) - 1)])

    logger.debug(f"Parsed CLI arguments: {cli_args}")
    logger.debug(f"Path to config files: {CONFIG_FILES}")

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILES)

    dispatch(cfg, cli_args)


if __name__ == "__main__":
    run()
