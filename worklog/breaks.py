from typing import List
from datetime import timedelta


class AutoBreak(object):
    _durations: List[int] = []
    _limits: List[int] = []

    def __init__(self, limits: List[int] = [], durations: List[int] = []):
        if len(limits) != len(durations):
            raise ValueError("limits and durations must have the same shape.")

        self._limits = limits
        self._durations = durations

    @property
    def active(self):
        return len(self._durations) > 0

    def get_duration(self, td: timedelta):
        """Calculate the break duration for a given timedelta."""
        if not self.active:
            return timedelta(minutes=0)

        full_minutes: int = int(td.total_seconds()) // 60

        break_duration = 0

        for i, limit in enumerate(self._limits):
            if limit > full_minutes:
                break
            break_duration = self._durations[i]

        return timedelta(minutes=break_duration)

