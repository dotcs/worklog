from typing import List, Iterable, Tuple, Dict, Optional, Union
from pandas import DataFrame, Series  # type: ignore
import logging
import sys
import argparse
import os
from functools import reduce
from datetime import datetime, date, timezone, timedelta, tzinfo
import shutil
from math import floor
import numpy as np

import worklog.constants as wc


def configure_logger() -> logging.Logger:
    logger = logging.getLogger(wc.DEFAULT_LOGGER_NAME)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(wc.LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def format_timedelta(td: timedelta) -> str:
    try:
        total_secs = td.total_seconds()
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    except (AttributeError, ValueError):
        return "{:02}:{:02}:{:02}".format(0, 0, 0)


def empty_df_from_schema(schema: Iterable[Tuple[str, str]]) -> DataFrame:
    def reducer(acc: Dict, x: Tuple[str, str]):
        acc[x[0]] = Series(dtype=x[1])
        return acc

    return DataFrame(reduce(reducer, schema, {}))


def get_datetime_cols_from_schema(schema: Iterable[Tuple[str, str]]) -> List[str]:
    def reducer(acc: List, x: Tuple[str, str]):
        if "datetime" in x[1]:
            acc.append(x[0])
        return acc

    return reduce(reducer, schema, [])


def check_order_session(df_group: DataFrame, logger: logging.Logger):
    last_type = None
    for i, row in df_group.where(
        df_group[wc.COL_CATEGORY] == wc.TOKEN_SESSION
    ).iterrows():
        if i == 0 and row[wc.COL_TYPE] != wc.TOKEN_START:
            logger.error(
                f'First entry of type "{wc.TOKEN_SESSION}" on date {row.date} is not "{wc.TOKEN_START}".'
            )
        if row[wc.COL_TYPE] == last_type:
            logger.error(
                f'"{wc.TOKEN_SESSION}" entries on date {row.date} are not ordered correctly.'
            )
        last_type = row[wc.COL_TYPE]
    if last_type != wc.TOKEN_STOP:
        logger.error(f"Date {row.date} has no stop entry.")


def sentinel_datetime(
    target_date: date, tzinfo: Optional[tzinfo] = wc.LOCAL_TIMEZONE
) -> datetime:
    if target_date > datetime.now().date():
        raise ValueError("Only dates on the same day or in the past are supported.")
    return min(
        datetime.now(timezone.utc).astimezone(tz=tzinfo).replace(microsecond=0),
        datetime(
            target_date.year, target_date.month, target_date.day, 23, 59, 59, 0, tzinfo,
        ).astimezone(tz=tzinfo),
    )


def calc_task_durations(
    df: DataFrame, keep_cols: List[str] = [wc.COL_TASK_IDENTIFIER, "time"]
):
    return df.groupby(wc.COL_TASK_IDENTIFIER).apply(
        lambda group: _calc_single_task_duration(group, keep_cols=keep_cols)
    )


def _calc_single_task_duration(df: DataFrame, keep_cols: List[str] = []):
    """
    Calculate the duration of a single task. The given DataFrame can consist
    of many log entries but all must have the same task identifier.
    """
    # TODO: Sanity check missing: Each start row should have a
    # corresponding stop row
    # TODO: Generalize this idea to other parts where time is calculated
    df = df.sort_values([wc.COL_LOG_DATETIME, wc.COL_TYPE])
    stop_mask = df[wc.COL_TYPE] == wc.TOKEN_STOP
    shifted_dt = df[wc.COL_LOG_DATETIME].shift(1)
    s_time = df[stop_mask][wc.COL_LOG_DATETIME] - shifted_dt[stop_mask]

    df_result = df[stop_mask].copy()
    df_result["time"] = s_time
    df_result = df_result.sort_values(by=[wc.COL_TASK_IDENTIFIER])
    return df_result[keep_cols]


def get_all_task_ids_with_duration(df: DataFrame):
    df = df[[wc.COL_LOG_DATETIME, wc.COL_TYPE, wc.COL_TASK_IDENTIFIER]].sort_values(
        by=[wc.COL_LOG_DATETIME]
    )

    df_h = calc_task_durations(df)
    s = df_h["time"]
    s.index = df_h.index.map(lambda k: k[0])
    return s.to_dict()


def get_active_task_ids(df: DataFrame):
    df = df[[wc.COL_LOG_DATETIME, wc.COL_TYPE, wc.COL_TASK_IDENTIFIER]].sort_values(
        by=[wc.COL_LOG_DATETIME]
    )

    df_grouped = df.groupby(wc.COL_TASK_IDENTIFIER).tail(1)
    return sorted(
        df_grouped[df_grouped[wc.COL_TYPE] == wc.TOKEN_START][
            wc.COL_TASK_IDENTIFIER
        ].unique()
    )


def extract_intervals(
    df: DataFrame,
    dt_col: str = wc.COL_LOG_DATETIME,
    TOKEN_START: str = wc.TOKEN_START,
    TOKEN_STOP: str = wc.TOKEN_STOP,
    logger: Optional[logging.Logger] = None,
):
    def log_error(msg):
        if logger:
            logger.error(msg)

    intervals = []
    last_start: Optional[datetime] = None
    for i, row in df.iterrows():
        if row[wc.COL_TYPE] == TOKEN_START:
            if last_start is not None:
                log_error(f"Start entry at {last_start} has no stop entry. Skip entry.")
            last_start = row[dt_col]
        elif row[wc.COL_TYPE] == TOKEN_STOP:
            if last_start is None:
                log_error("No start entry found. Skip entry.")
                continue  # skip this entry
            td = row[dt_col] - last_start
            d = last_start.date()
            intervals.append(
                {"date": d, "start": last_start, "stop": row[dt_col], "interval": td}
            )
            last_start = None
        else:
            log_error(f"Found unknown type {row['type']}. Skip entry.")
            continue
    if last_start is not None:
        log_error(f"Start entry at {last_start} has no stop entry. Skip entry.")

    return DataFrame(intervals)


def get_pager() -> Optional[str]:
    # Windows comes pre-installed with the 'more' pager.
    # See https://superuser.com/a/426229
    # Unix distributions also have 'more' pre-installed.
    more_bin = shutil.which("more")
    less_bin = shutil.which("less")
    default_pager = more_bin
    if less_bin is not None:
        default_pager = less_bin
    pager = os.getenv("PAGER", default_pager)
    return pager


def _get_or_update_dt(dt: datetime, time: str):
    try:
        h_time = datetime.strptime(time, "%H:%M")
        hour, minute = h_time.hour, h_time.minute
        return dt.replace(hour=hour, minute=minute, second=0)
    except ValueError:
        h_time = datetime.fromisoformat(time)
        if h_time.tzinfo is None:
            # Set local timezone if not defined explicitly.
            h_time = h_time.replace(tzinfo=wc.LOCAL_TIMEZONE)
        return h_time


def calc_log_time(offset_min: int = 0, time: Optional[str] = None) -> datetime:
    """
    Calculates the log time based on the current timestamp and either an
    offset or a time correction.
    """
    my_date = datetime.now(timezone.utc).astimezone().replace(microsecond=0)
    my_date = my_date + timedelta(minutes=offset_min)

    if time is not None:
        my_date = _get_or_update_dt(my_date, time)

    return my_date


def format_numpy_timedelta(value: np.timedelta64) -> str:
    seconds = value / np.timedelta64(1, "s")
    if np.isnan(seconds):
        hours = minutes = seconds = 0
    else:
        hours = floor(seconds / 3600)
        minutes = floor((seconds - hours * 3600) / 60)
        seconds = floor(seconds % 60)
    return "{hours:02}:{minutes:02}:{seconds:02}".format(
        hours=hours, minutes=minutes, seconds=seconds
    )
