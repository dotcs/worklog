import unittest
from datetime import timedelta

from worklog.breaks import BreakConfig


class TestBreaks(unittest.TestCase):
    def test_zero(self):
        td = timedelta(minutes=0)
        break_cfg = BreakConfig()

        expected = 0
        actual = break_cfg.calc_break_duration(td).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_nonequal_list_lens(self):
        limits = [0, 360]  # len: 2
        durations = [15]  # len: 1

        with self.assertRaises(ValueError):
            break_cfg = BreakConfig(limits, durations)

    def test_in_first_interval(self):
        limits = [0, 360]  # in minutes
        durations = [15, 45]  # in minutes
        break_cfg = BreakConfig(limits, durations)

        td = timedelta(minutes=5)
        expected = 15

        actual = break_cfg.calc_break_duration(td).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_above_first_interval(self):
        limits = [0, 360]  # in minutes
        durations = [15, 45]  # in minutes
        break_cfg = BreakConfig(limits, durations)

        td = timedelta(minutes=361)
        expected = 45
        actual = break_cfg.calc_break_duration(td).total_seconds() // 60

        self.assertEqual(expected, actual)

    def test_in_mid_interval(self):
        limits = [0, 200, 360]  # in minutes
        durations = [15, 20, 45]  # in minutes
        break_cfg = BreakConfig(limits, durations)

        td = timedelta(minutes=201)
        expected = 20
        actual = break_cfg.calc_break_duration(td).total_seconds() // 60

        self.assertEqual(expected, actual)
