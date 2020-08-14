import logging
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from io import StringIO
from math import floor
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from worklog.breaks import AutoBreak
from worklog.constants import (
    COL_CATEGORY,
    COL_COMMIT_DATETIME,
    COL_LOG_DATETIME,
    COL_TASK_IDENTIFIER,
    COL_TYPE,
    DEFAULT_LOGGER_NAME,
    LOCAL_TIMEZONE,
    TOKEN_SESSION,
    TOKEN_START,
    TOKEN_STOP,
    TOKEN_TASK,
)
from worklog.utils import (
    calc_log_time,
    check_order_session,
    empty_df_from_schema,
    extract_intervals,
    format_timedelta,
    get_active_task_ids,
    get_all_task_ids,
    get_datetime_cols_from_schema,
    get_pager,
    sentinel_datetime,
    format_numpy_timedelta,
)

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


class Log(object):
    # In-memory representation of log
    _log_df: pd.DataFrame = None

    # Backend file config
    _log_fp: Optional[str] = None
    _separator: Optional[str] = None
    _schema: List[Tuple[str, str]] = [
        (COL_COMMIT_DATETIME, "datetime64[ns]",),
        (COL_LOG_DATETIME, "datetime64[ns]",),
        (COL_CATEGORY, "object",),
        (COL_TYPE, "object",),
        (COL_TASK_IDENTIFIER, "object",),
    ]

    # Error messages
    _err_msg_empty_log = (
        "Fatal: No log data available. Start a new log entry with 'wl commit start'.\n"
    )
    _err_msg_empty_log_short = "N/A"
    _err_msg_log_data_missing_for_date = "No log data available for {query_date}.\n"
    _err_msg_log_data_missing_for_date_short = "N/A"
    _err_msg_commit_active_tasks = (
        "Fatal. Cannot stop, because tasks are still running. "
        "Stop running tasks first: {active_tasks:} or use --force flag.\n"
    )

    auto_break: AutoBreak = AutoBreak()

    def __init__(self, fp: str, separator: str = "|") -> None:
        self._log_fp = fp
        self._separator = separator

        Path(self._log_fp).touch(mode=0o660)
        self._read()

    def commit(
        self,
        category: str,
        type_: str,
        offset_min: int = 0,
        time: Optional[str] = None,
        identifier: str = None,
        force: bool = False,
    ) -> None:
        """Commit a session/task change to the logfile."""
        log_date = calc_log_time(offset_min, time)
        self._commit(category, type_, log_date, identifier, force)

    def doctor(self) -> None:
        """Test if the logfile is consistent."""
        self._log_df.groupby(["date"]).apply(
            lambda group: check_order_session(group, logger)
        )

    def list_tasks(self):
        """List all known tasks, i.e. tasks that have been used previously
        and are stored in the logfile."""
        task_df = self._log_df[self._log_df[COL_CATEGORY] == TOKEN_TASK]
        sys.stdout.write("These tasks are listed in the log:\n")
        for task_id in sorted(task_df[COL_TASK_IDENTIFIER].unique()):
            sys.stdout.write(f"{task_id}\n")

    def log(self, n: int, use_pager: bool, filter_category: List[str]) -> None:
        """Display the content of the logfile."""
        if self._log_df.shape[0] == 0:
            sys.stdout.write("No data available\n")
            return

        fields = ["date", "time", COL_CATEGORY, COL_TYPE, COL_TASK_IDENTIFIER]
        df = self._log_df[fields].iloc[::-1]  # sort in reverse (latest first)
        df[COL_TASK_IDENTIFIER] = df[COL_TASK_IDENTIFIER].fillna("-")
        if filter_category:
            df = df[df[COL_CATEGORY] == filter_category]
        if n > 0:
            df = df.head(n=n)
        if not use_pager:
            sys.stdout.write(df.to_string(index=False) + "\n")
        else:
            with tempfile.NamedTemporaryFile(mode="w") as fh:
                logger.debug(f"Write content to temporary file: {fh.name}")
                fh.write(df.to_string(index=False))
                fh.flush()
                pager = get_pager()
                if pager is None:
                    sys.stdout.write(df.to_string(index=False) + "\n")
                else:
                    logger.debug(f"Set pager to {pager}")
                    process = subprocess.Popen([pager, fh.name])
                    process.wait()

    def report(self, month_from: datetime, month_to: datetime):
        """Generate a daily, weekly, monthly and task based report based on
        the content in the logfile."""
        session_mask = self._log_df[COL_CATEGORY] == TOKEN_SESSION
        task_mask = self._log_df[COL_CATEGORY] == TOKEN_TASK
        time_mask = (self._log_df[COL_LOG_DATETIME] >= month_from) & (
            self._log_df[COL_LOG_DATETIME] < month_to
        )

        # Day aggregation
        df_day = self._aggregate_time(time_mask & session_mask, resample="D")
        df_day["break"] = df_day["agg_time"].map(self.auto_break.get_duration)

        # Week aggregation
        df_week = df_day.set_index(COL_LOG_DATETIME).resample("W").sum().reset_index()

        # Month aggregration
        df_month = df_day.set_index(COL_LOG_DATETIME).resample("M").sum().reset_index()

        for df in (df_day, df_week, df_month):
            df["agg_time_bookable"] = df["agg_time"] - df["break"]

        # Task aggregation
        df_tasks = self._aggregate_tasks(time_mask & task_mask)

        print_cols = [COL_LOG_DATETIME, "agg_time"]
        print_cols_labels = ["Date", "Total time"]
        if self.auto_break.active:
            print_cols += ["break", "agg_time_bookable"]
            print_cols_labels += ["Break", "Bookable time"]

        def _formatters(date: str = "M"):
            date_max_len = len("2000-01") if date == "M" else len("2000-01-01")
            return {
                COL_LOG_DATETIME: lambda v: str(v.date())[:date_max_len],
                "agg_time": format_numpy_timedelta,
                "agg_time_bookable": format_numpy_timedelta,
            }

        self._print_aggregation(
            "month",
            df_month,
            print_cols,
            print_cols_labels,
            formatters=_formatters("M"),
        )
        self._print_aggregation(
            "week", df_week, print_cols, print_cols_labels, formatters=_formatters("D"),
        )
        self._print_aggregation(
            "day", df_day, print_cols, print_cols_labels, formatters=_formatters("D")
        )

        print_cols = [COL_TASK_IDENTIFIER, "agg_time"]
        print_cols_labels = ["Task name", "Total time"]
        self._print_aggregation("tasks", df_tasks, print_cols, print_cols_labels)

    def status(
        self, hours_target: float, hours_max: float, query_date: date, fmt: str = None,
    ) -> None:
        """Display the current working status, e.g. total time worked at this
        day, remaining time, etc."""
        self._check_nonempty_or_exit(fmt)

        df_day = self._filter_date_category_limit_cols(query_date)

        if df_day.shape[0] == 0:
            if fmt is None:
                msg = self._err_msg_log_data_missing_for_date.format(
                    query_date=query_date
                )
                sys.stderr.write(msg)
            else:
                sys.stdout.write(self._err_msg_log_data_missing_for_date_short)
            return

        is_active = self._is_active(df_day)
        logger.debug(f"Is active: {is_active}")

        df_day = self._add_sentinel(query_date, df_day)
        facts = self._calc_facts(df_day, hours_target, hours_max)

        all_touched_tasks = get_all_task_ids(self._log_df, query_date)
        active_tasks = get_active_task_ids(self._log_df, query_date)

        lines = [
            ("Status", "Tracking {status}"),
            ("Total time", "{total_time} ({percentage:3}%)"),
            ("Remaining time", "{remaining_time} ({percentage_remaining:3}%)"),
            ("Overtime", "{overtime} ({percentage_overtime:3}%)"),
            ("Break Duration", "{break_duration}"),
            ("All touched tasks", "{all_touched_tasks}",),
            ("Active tasks", "{active_tasks}",),
        ]

        if is_active and date == "today":
            lines += [("End of work", facts["end_time_str"],)]

        key_max_len = max([len(line[0]) for line in lines])
        fmt_string = "{:" + str(key_max_len + 1) + "s}: {}"

        stdout_fmt = "\n".join(fmt_string.format(*line) for line in lines) + "\n"

        sys.stdout.write(
            (stdout_fmt if fmt is None else fmt).format(
                **facts,
                status="on" if is_active else "off",
                active_tasks=f"({len(active_tasks)}) [" + ", ".join(active_tasks) + "]",
                all_touched_tasks=f"({len(all_touched_tasks)}) ["
                + ", ".join(all_touched_tasks)
                + "]",
            )
        )

    def stop_active_tasks(self, log_dt: datetime):
        """Stop all active tasks by commiting changes to the logfile."""
        query_date = log_dt.date()
        active_task_ids = get_active_task_ids(self._log_df, query_date)
        for task_id in active_task_ids:
            self._commit(TOKEN_TASK, TOKEN_STOP, log_dt, identifier=task_id)

    def task_report(self, task_id):
        """Generate a report of a given task."""
        task_mask = self._log_df[COL_CATEGORY] == TOKEN_TASK
        task_id_mask = self._log_df[COL_TASK_IDENTIFIER] == task_id
        mask = task_mask & task_id_mask
        task_df = self._log_df[mask]

        if task_df.shape[0] == 0:
            sys.stderr.write(
                (
                    f"Task ID {task_id} is unknown. "
                    "See 'wl task list' to list all known tasks.\n"
                )
            )
            exit(1)

        intervals = extract_intervals(task_df, logger=logger)

        intervals_detailed = intervals[["date", "start", "stop", "interval"]].rename(
            columns={
                "date": "Date",
                "start": "Start",
                "stop": "Stop",
                "interval": "Duration",
            }
        )
        print("Log entries:\n")
        print(
            intervals_detailed.to_string(
                index=False,
                formatters={
                    "Start": lambda x: x.strftime("%H:%M:%S"),
                    "Stop": lambda x: x.strftime("%H:%M:%S"),
                    "Duration": lambda x: format_timedelta(
                        timedelta(microseconds=int(x) / 1e3)
                    ),
                },
            )
        )

        print("---")
        print("Daily aggregated:\n")
        intervals_daily = intervals.groupby(by="date")[["interval"]].sum()
        intervals_daily.index.name = "Date"
        intervals_daily = intervals_daily.rename(columns={"interval": "Duration"})
        print(intervals_daily.to_string())

        print(f"---\nTotal: {intervals_detailed['Duration'].sum()}")

    def _read(self) -> None:
        """
        Read data from input file.
        This method uses `pandas.read_csv` to parse the data.
        """
        date_cols = get_datetime_cols_from_schema(self._schema)
        header = [col for col, _ in self._schema]
        try:
            self._log_df = pd.read_csv(
                self._log_fp,
                sep=self._separator,
                parse_dates=date_cols,
                header=None,
                names=header,
            ).sort_values(by=[COL_LOG_DATETIME])
        except pd.errors.EmptyDataError:
            self._log_df = empty_df_from_schema(self._schema)

        self._log_df = pd.concat(
            [self._log_df, self._extract_date_and_time(self._log_df)], axis=1
        )

    def _extract_date_and_time(
        self, df: pd.DataFrame, source_col: str = COL_LOG_DATETIME
    ) -> pd.DataFrame:
        """
        Extracts date and time information from a given pandas DataFrame.
        By default the source column is `log_dt`.
        """
        date: pd.Series = df[source_col].apply(lambda x: x.date)
        time: pd.Series = df[source_col].apply(lambda x: x.time)
        return pd.DataFrame(dict(date=date, time=time),)

    def _persist(self, df: pd.DataFrame, mode="a") -> None:
        cols = [col for col, _ in self._schema]
        df[cols].to_csv(
            self._log_fp, mode=mode, sep=self._separator, index=False, header=False
        )

    def _commit(
        self,
        category: str,
        type_: str,
        log_dt: datetime,
        identifier: str = None,
        force: bool = False,
    ) -> None:
        if type_ not in [TOKEN_START, TOKEN_STOP]:
            raise ValueError(
                f'Type must be one of {", ".join([TOKEN_START, TOKEN_STOP])}'
            )

        commit_dt = datetime.now(timezone.utc).astimezone().replace(microsecond=0)

        # Test if there are running tasks
        if category == TOKEN_SESSION:
            active_tasks = get_active_task_ids(self._log_df, log_dt.date())
            if len(active_tasks) > 0:
                if not force:
                    msg = self._err_msg_commit_active_tasks.format(
                        active_tasks=active_tasks
                    )
                    sys.stderr.write(msg)
                    sys.exit(1)
                else:
                    for task_id in active_tasks:
                        self._commit(TOKEN_TASK, TOKEN_STOP, log_dt, task_id)

        cols = [col for col, _ in self._schema]
        values = [
            pd.to_datetime(commit_dt),
            pd.to_datetime(log_dt),
            category,
            type_,
            identifier,
        ]

        record = pd.DataFrame(dict(zip(cols, values)), index=[0],)
        record_t = pd.concat([record, self._extract_date_and_time(record)], axis=1)

        # append record to in-memory log
        self._log_df = pd.concat((self._log_df, record_t))
        # and persist to disk
        self._persist(record_t, mode="a")

        # Because we allow for time offsets sorting is not guaranteed at this point.
        # Update sorting of values in-memory.
        self._log_df = self._log_df.sort_values(by=[COL_LOG_DATETIME])

    def _is_active(self, df: pd.DataFrame):
        """
        Returns True if the last entry in a given pandas DataFrame has 
        `type == 'start'`.

        Note: This method does not check for anything else. If this should
        just be applied to a single category, make sure to filter the pandas
        DataFrame first.
        """
        return df.iloc[-1][COL_TYPE] == TOKEN_START if df.shape[0] > 0 else False

    def _check_nonempty_or_exit(self, fmt: Optional[str]):
        """
        Tests if the log file has at least a single value.
        Exits with code 0 if no entry is available.
        """
        if self._log_df.shape[0] == 0:
            if fmt is None:
                sys.stderr.write(self._err_msg_empty_log)
            else:
                sys.stdout.write(self._err_msg_empty_log_short)
            sys.exit(0)

    def _filter_date_category_limit_cols(
        self,
        query_date: date,
        filter_category: str = TOKEN_SESSION,
        columns: List[str] = [COL_LOG_DATETIME, COL_TYPE],
    ):
        """
        Filters the worklog DataFrame by query date and category.
        The returned DataFrame only includes the columns listed in the
        `columns` parameter.
        """
        # Extract the day of interest by selecting a subset of the log
        # dataframe that matches the queried day.
        mask = (self._log_df.date == query_date) & (
            self._log_df.category == filter_category
        )
        df = self._log_df[mask]
        df = df[columns]
        return df

    def _add_sentinel(self, query_date: date, df: pd.DataFrame):
        is_active = self._is_active(df)
        ret = df
        if is_active:
            sdt = sentinel_datetime(query_date)
            # attach another row with the current time
            sentinel_df = pd.DataFrame(
                {
                    COL_LOG_DATETIME: pd.to_datetime(sdt.isoformat()),
                    COL_TYPE: TOKEN_STOP,
                },
                index=[0],
            )
            ret = pd.concat((ret, sentinel_df))
            logger.warning(f"Set sentinel stop value: {sdt}")
        return ret

    def _calc_facts(self, df: pd.DataFrame, hours_target: float, hours_max: float):
        shifted_dt = df[COL_LOG_DATETIME].shift(1)
        stop_mask = df[COL_TYPE] == TOKEN_STOP
        total_time = (df[stop_mask][COL_LOG_DATETIME] - shifted_dt[stop_mask]).sum()
        total_time_str = format_timedelta(total_time)

        break_duration = self.auto_break.get_duration(total_time)

        hours_target_dt = timedelta(hours=hours_target) + break_duration
        hours_max_dt = timedelta(hours=hours_max) + break_duration

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
        return dict(
            percentage=percentage,
            end_of_work=end_time_str,
            total_time=total_time_str,
            remaining_time=remaining_time_str,
            remaining_time_short=remaining_time_str[: len("00:00")],
            percentage_remaining=percentage_remaining,
            overtime=overtime_str,
            overtime_short=overtime_str[: len("00:00")],
            percentage_overtime=percentage_overtime,
            break_duration=format_timedelta(break_duration),
        )

    def _aggregate_base(self, mask, keep_cols: List[str] = []):
        df = self._log_df[mask]
        shifted_dt = df[COL_LOG_DATETIME].shift(1)
        stop_mask = df[COL_TYPE] == TOKEN_STOP
        agg_time = df[stop_mask][COL_LOG_DATETIME] - shifted_dt[stop_mask]
        ret = df[stop_mask][[COL_LOG_DATETIME] + keep_cols]
        ret["agg_time"] = agg_time
        return ret

    def _aggregate_time(self, mask, resample="D"):
        df = self._aggregate_base(mask, keep_cols=["date"])
        df_day = (
            df.set_index(COL_LOG_DATETIME)
            .resample(resample)
            .sum()
            .reset_index()
            .dropna()
        )
        return df_day

    def _aggregate_tasks(self, mask):
        df = self._aggregate_base(mask, keep_cols=[COL_TASK_IDENTIFIER])
        return (
            df.set_index(COL_LOG_DATETIME)
            .groupby(COL_TASK_IDENTIFIER)
            .sum()
            .reset_index()
        )

    def _print_aggregation(self, agg_label, df, cols, col_titles, formatters=None):
        headline = f"Aggregated by {agg_label}:"
        print(headline)
        print("-" * len(headline))
        print(
            df.to_string(
                index=False,
                columns=cols,
                header=col_titles,
                formatters=formatters,
                col_space=20,
            )
        )

        print()
