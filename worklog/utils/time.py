from typing import Optional
from datetime import datetime, timedelta, timezone
import pandas as pd

import worklog.constants as wc


def _get_or_update_dt(dt: datetime, time: str):
    try:
        h_time = datetime.strptime(time, "%H:%M")
        hour, minute = h_time.hour, h_time.minute
        return dt.replace(hour=hour, minute=minute, second=0)
    except ValueError:
        h_time = datetime.fromisoformat(time).replace(second=0)
        if h_time.tzinfo is None:
            # Set local timezone if not defined explicitly.
            h_time = h_time.replace(tzinfo=wc.LOCAL_TIMEZONE)
        return h_time


def calc_log_time(offset_min: int = 0, time: Optional[str] = None) -> datetime:
    """
    Calculates the log time based on the current timestamp and either an
    offset or a time correction.
    """
    my_date = (
        datetime.now(timezone.utc)
        .astimezone(tz=wc.LOCAL_TIMEZONE)
        .replace(microsecond=0)
    )
    my_date = my_date + timedelta(minutes=offset_min)

    if time is not None:
        my_date = _get_or_update_dt(my_date, time)

    return my_date


def extract_date_and_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts date and time information from a given pandas DataFrame.
    By default the source column is `log_dt`.
    """
    log_dt: pd.Series = df[wc.COL_LOG_DATETIME].apply(
        lambda x: x.astimezone(timezone.utc)
    )
    commit_dt: pd.Series = df[wc.COL_COMMIT_DATETIME].apply(
        lambda x: x.astimezone(timezone.utc)
    )
    date: pd.Series = df[wc.COL_LOG_DATETIME].apply(lambda x: x.date())
    time: pd.Series = df[wc.COL_LOG_DATETIME].apply(lambda x: x.timetz())

    return pd.DataFrame(
        {
            "date": date,
            "time": time,
            wc.COL_LOG_DATETIME_UTC: log_dt,
            wc.COL_COMMIT_DATETIME_UTC: commit_dt,
        }
    )


def now_localtz() -> datetime:
    return (
        datetime.now(timezone.utc)
        .astimezone(tz=wc.LOCAL_TIMEZONE)
        .replace(microsecond=0)
    )

