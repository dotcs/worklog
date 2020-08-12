from typing import List
from datetime import timedelta


def calc_break_duration(
    td: timedelta, limits: List[int] = [], durations: List[int] = []
):
    if len(limits) != len(durations):
        raise ValueError("limits and durations must have the same shape.")

    full_minutes: int = int(td.total_seconds()) // 60

    break_duration = 0

    for i, limit in enumerate(limits):
        if limit > full_minutes:
            break
        break_duration = durations[i]

    return timedelta(minutes=break_duration)

