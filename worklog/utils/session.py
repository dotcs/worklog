from typing import Optional
from pandas import DataFrame
from datetime import datetime, date, timezone, tzinfo
import logging

import worklog.constants as wc


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


def is_active_session(df: DataFrame):
    """
    Returns True if the last entry in a given pandas DataFrame has the
    category 'session' and type 'start'.

    Note: Make sure to apply this method only on a sorted DataFrame.
    """
    return df.iloc[-1][wc.COL_TYPE] == wc.TOKEN_START if df.shape[0] > 0 else False
