from typing import Union, Optional
from datetime import timedelta
import pandas as pd
import numpy as np
from math import floor


def format_timedelta(value: Optional[Union[timedelta, np.timedelta64]]) -> str:
    if value is None or value is pd.NaT or value is np.nan:
        return "{:02}:{:02}:{:02}".format(0, 0, 0)
    elif isinstance(value, timedelta):
        return _format_timedelta_py(value)
    elif isinstance(value, np.timedelta64):
        return _format_timedelta_np(value)
    else:
        raise ValueError("value must be either a Python or a numpy timedelta instance")


def _format_timedelta_py(td: timedelta) -> str:
    try:
        total_secs = td.total_seconds()
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    except (AttributeError, ValueError):
        return "{:02}:{:02}:{:02}".format(0, 0, 0)


def _format_timedelta_np(value: np.timedelta64) -> str:
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
