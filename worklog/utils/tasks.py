from typing import List, Optional
from pandas import DataFrame
from datetime import datetime
import logging

import worklog.constants as wc


def calc_task_durations(
    df: DataFrame, keep_cols: List[str] = [wc.COL_TASK_IDENTIFIER, "time"]
) -> DataFrame:
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
    if df_h.empty:
        return {}
    s = df_h["time"]
    s.index = df_h.index.map(lambda k: k[0])
    return s.to_dict()


def get_active_task_ids(df: DataFrame):
    """
    Returns a list of active tasks.
    Note: This method can only handle DataFrames that have entries where the
    category is set to 'task'.
    """
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
    df: DataFrame, logger: Optional[logging.Logger] = None,
):
    def log_error(msg):
        if logger:
            logger.error(msg)

    intervals = []
    last_start: Optional[datetime] = None
    for i, row in df.iterrows():
        if row[wc.COL_TYPE] == wc.TOKEN_START:
            if last_start is not None:
                log_error(f"Start entry at {last_start} has no stop entry. Skip entry.")
            last_start = row[wc.COL_LOG_DATETIME]
        elif row[wc.COL_TYPE] == wc.TOKEN_STOP:
            if last_start is None:
                log_error("No start entry found. Skip entry.")
                continue  # skip this entry
            td = row[wc.COL_LOG_DATETIME] - last_start
            d = last_start.date()
            intervals.append(
                {
                    "date": d,
                    "start": last_start,
                    "stop": row[wc.COL_LOG_DATETIME],
                    "interval": td,
                }
            )
            last_start = None
        else:
            log_error(f"Found unknown type '{row['type']}'. Skip entry.")
            continue
    if last_start is not None:
        log_error(f"Start entry at {last_start} has no stop entry. Skip entry.")

    return DataFrame(intervals, columns=["date", "start", "stop", "interval"])
