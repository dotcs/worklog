import unittest
from datetime import timedelta

from worklog.breaks import calc_break_duration


class TestBreaks(unittest.TestCase):
    def test_zero(self):
        td = timedelta(minutes=0)
        expected = 0
        actual = calc_break_duration(td).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_nonequal_list_lens(self):
        td = timedelta(minutes=0)
        limits = [0, 360]  # len: 2
        durations = [15]  # len: 1

        with self.assertRaises(ValueError):
            calc_break_duration(td, limits, durations).total_seconds() // 60

    def test_in_first_interval(self):
        limits = [0, 360]  # in minutes
        durations = [15, 45]  # in minutes

        td = timedelta(minutes=5)
        expected = 15
        actual = calc_break_duration(td, limits, durations).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_above_first_interval(self):
        limits = [0, 360]  # in minutes
        durations = [15, 45]  # in minutes

        td = timedelta(minutes=361)
        expected = 45
        actual = calc_break_duration(td, limits, durations).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_in_mid_interval(self):
        limits = [0, 200, 360]  # in minutes
        durations = [15, 20, 45]  # in minutes

        td = timedelta(minutes=201)
        expected = 20
        actual = calc_break_duration(td, limits, durations).total_seconds() // 60

        self.assertEqual(expected, actual)
