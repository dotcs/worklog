from typing import List, Tuple
from datetime import datetime, timedelta, timezone
import logging
import os
import sys
import pandas as pd
import numpy as np
import subprocess
import tempfile
from pathlib import Path

from worklog.utils import (
    LOCAL_TIMEZONE,
    format_timedelta,
    empty_df_from_schema,
    get_datetime_cols_from_schema,
)

logger = logging.getLogger("worklog")


class Log(object):
    _log_fp: str = None
    _log_df: pd.DataFrame = None
    _separator: str = None
    _schema: List[Tuple[str, str]] = [
        ("datetime", "datetime64[ns]",),
        ("category", "object",),
        ("type", "object",),
    ]

    def __init__(self, fp: str, separator: str = "|") -> None:
        self._log_fp = fp
        self._separator = separator

        Path(self._log_fp).touch(mode=0o660)
        self._read()

    def _read(self) -> None:
        date_cols = get_datetime_cols_from_schema(self._schema)
        try:
            self._log_df = pd.read_csv(
                self._log_fp, sep=self._separator, parse_dates=date_cols
            )
        except pd.errors.EmptyDataError:
            self._log_df = empty_df_from_schema(self._schema)

        self._log_df["date"] = self._log_df["datetime"].apply(lambda x: x.date)
        self._log_df["time"] = self._log_df["datetime"].apply(lambda x: x.time)

    def _persist(self, df: pd.DataFrame, reload: bool = False) -> None:
        persisted_fields = [key for key, _ in self._schema]
        df[persisted_fields].sort_values(by=["datetime"], ascending=True).to_csv(
            self._log_fp, sep=self._separator, index=False
        )
        if reload:
            self._read()

    def commit(self, type_: str, offset_min: int) -> None:
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

    def doctor(self) -> None:
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

    def status(
        self, hours_target: int, hours_max: int, date: str = "today", fmt: str = None
    ) -> None:
        if self._log_df.shape[0] == 0:
            if fmt is None:
                sys.stderr.write(
                    "Fatal: No log data available. Start a new log entry with 'wl commit start'.\n"
                )
            else:
                sys.stdout.write("N/A")
            return

        query_date = datetime.now().date()
        if date == "yesterday":
            query_date -= timedelta(days=1)

        sub_df = self._log_df[self._log_df.date == query_date]
        sub_df = sub_df[["datetime", "type"]]

        if sub_df.shape[0] == 0:
            if fmt is None:
                sys.stderr.write(f"No log data available for {query_date}.\n")
            else:
                sys.stdout.write("N/A")
            return

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
        total_time_str = format_timedelta(total_time)

        hours_target_dt = timedelta(hours=hours_target)
        hours_max_dt = timedelta(hours=hours_max)

        now = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
        end_time = now + (hours_target_dt - total_time)
        end_time_str = end_time.strftime("%H:%M:%S")
        remaining_time = max(end_time - now, timedelta(minutes=0))
        remaining_time_str = format_timedelta(remaining_time)
        overtime = max(total_time - hours_target_dt, timedelta(minutes=0))
        overtime_str = format_timedelta(overtime)

        percentage = round(
            total_time.total_seconds() / hours_target_dt.total_seconds() * 100
        )
        percentage_remaining = max(0, 100 - percentage)
        percentage_overtime = max(
            round(
                overtime.total_seconds()
                / (hours_max_dt - hours_target_dt).total_seconds()
                * 100
            ),
            0,
        )

        lines = [
            ("Status", "Tracking on" if is_curr_working else "Tracking off"),
            ("Total time", "{} ({:3}%)".format(total_time_str, percentage)),
            (
                "Remaining time",
                "{} ({:3}%)".format(remaining_time_str, percentage_remaining),
            ),
            ("Overtime", "{} ({:3}%)".format(overtime_str, percentage_overtime),),
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
                    remaining_time_short=remaining_time_str[: len("00:00")],
                    percentage_remaining=percentage_remaining,
                    overtime=overtime_str,
                    overtime_short=overtime_str[: len("00:00")],
                    percentage_overtime=percentage_overtime,
                )
            )

    def log(self, n: int, use_pager: bool) -> None:
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
