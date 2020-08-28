from datetime import timedelta
import numpy as np
from math import floor


def format_timedelta(td: timedelta) -> str:
    try:
        total_secs = td.total_seconds()
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    except (AttributeError, ValueError):
        return "{:02}:{:02}:{:02}".format(0, 0, 0)


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
