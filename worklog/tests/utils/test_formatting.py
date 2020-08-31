import unittest
from datetime import timedelta
import numpy as np
import pandas as pd

from worklog.utils.formatting import format_timedelta


class TestTimeFormatting(unittest.TestCase):
    def test_invalid_value_none(self):
        expected = "00:00:00"

        td = None
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_invalid_value_nat(self):
        expected = "00:00:00"
        td = pd.NaT
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_invalid_value_nan(self):
        expected = "00:00:00"
        td = np.nan
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_default_behaviour(self):
        td = timedelta(hours=1, minutes=5, seconds=30)
        expected = "01:05:30"
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_format_timedelta_nat(self):
        """It should not break if a numpy not-a-time value is passed."""
        actual = format_timedelta(np.timedelta64("nAt"))
        expected = "00:00:00"

        self.assertEqual(actual, expected)

    def test_format_timedelta_valid(self):
        actual = format_timedelta(np.timedelta64(100, "s"))
        expected = "00:01:40"

        self.assertEqual(actual, expected)

    def test_format_timedelta_valid_days(self):
        actual = format_timedelta(np.timedelta64(2, "D"))
        expected = "48:00:00"

        self.assertEqual(actual, expected)

        actual = format_timedelta(np.timedelta64(20, "D"))
        expected = "480:00:00"

        self.assertEqual(actual, expected)
