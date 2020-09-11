from typing import Optional
from pandas import DataFrame, Series
import numpy as np
from datetime import datetime, date, timezone, tzinfo
import logging

import worklog.constants as wc
from worklog.errors import ErrMsg


def check_order_session(
    df_group: DataFrame, logger: logging.Logger, task_id: str = None
):
    mask_start = df_group[wc.COL_TYPE] == wc.TOKEN_START
    mask_stop = df_group[wc.COL_TYPE] == wc.TOKEN_STOP

    # Roll start_mask series n -> n+1, but keep the index the same.
    # This can be used to later compare if both, the shifted start_mask series
    # and the mask_stop series are the same, which must be the case if both
    # only contain alternating values as it should be in a healthy log.
    shifted_mask_start = Series(np.roll(mask_start.values, 1), index=mask_start.index)

    date = df_group.date.iloc[0]

    if mask_start.sum() < mask_stop.sum():
        if task_id is None:
            logger.error(
                ErrMsg.MISSING_SESSION_ENTRY.value.format(
                    type=wc.TOKEN_START, date=date
                )
            )
        else:
            logger.error(
                ErrMsg.MISSING_TASK_ENTRY.value.format(
                    type=wc.TOKEN_START, date=date, task_id=task_id
                )
            )
    elif mask_start.sum() > mask_stop.sum():
        if task_id is None:
            logger.error(
                ErrMsg.MISSING_SESSION_ENTRY.value.format(type=wc.TOKEN_STOP, date=date)
            )
        else:
            logger.error(
                ErrMsg.MISSING_TASK_ENTRY.value.format(
                    type=wc.TOKEN_STOP, date=date, task_id=task_id
                )
            )
    # First compare if the first entry is a start entry and then see if both
    # the shifted_start_mask series and the mask_stop series have the same
    # values. See above for an explanation.
    elif int(mask_start.iloc[0]) != 1 or not shifted_mask_start.equals(mask_stop):
        if task_id is None:
            logger.error(ErrMsg.WRONG_SESSION_ORDER.value.format(date=date))
        else:
            logger.error(
                ErrMsg.WRONG_TASK_ORDER.value.format(date=date, task_id=task_id)
            )


def sentinel_datetime(target_date: date) -> datetime:
    if target_date > datetime.now().date():
        raise ValueError("Only dates on the same day or in the past are supported.")
    return min(
        datetime.now(timezone.utc)
        .astimezone(tz=wc.LOCAL_TIMEZONE)
        .replace(microsecond=0),
        datetime(
            target_date.year,
            target_date.month,
            target_date.day,
            23,
            59,
            59,
            0,
            wc.LOCAL_TIMEZONE,
        ).astimezone(tz=wc.LOCAL_TIMEZONE),
    )


def is_active_session(df: DataFrame):
    """
    Returns True if the last entry in a given pandas DataFrame has the
    category 'session' and type 'start'.

    Note: Make sure to apply this method only on a sorted DataFrame.
    """
    return df.iloc[-1][wc.COL_TYPE] == wc.TOKEN_START if df.shape[0] > 0 else False
