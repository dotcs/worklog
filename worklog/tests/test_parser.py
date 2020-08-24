import unittest
from unittest.mock import patch
from io import StringIO
from argparse import ArgumentParser, ArgumentError, ArgumentTypeError
from datetime import datetime

from worklog.constants import LOCAL_TIMEZONE
from worklog.parser import (
    get_arg_parser,
    _positive_int,
    _combined_month_or_day_or_week_parser,
    _year_month_day_parser,
    _year_month_parser,
    _calendar_week_parser,
)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = get_arg_parser()

    def tearDown(self):
        self.parser = None

    def test_positive_int_with_pos_int(self):
        expected = 5
        actual = _positive_int("5")
        self.assertEqual(expected, actual)

    def test_positive_int_with_neg_int(self):
        with self.assertRaises(ArgumentTypeError):
            _positive_int("-5")

    def test_combined_month_or_day_or_week_parser_value_unknown(self):
        with self.assertRaises(ArgumentTypeError):
            _combined_month_or_day_or_week_parser("foobar")

    @patch("worklog.parser._year_month_parser")
    def test_combined_month_or_day_or_week_parser_ym(self, ym_mock):
        _combined_month_or_day_or_week_parser("2020-01")
        ym_mock.assert_called_with("2020-01")

    @patch("worklog.parser._year_month_day_parser")
    def test_combined_month_or_day_or_week_parser_ymd(self, ymd_mock):
        _combined_month_or_day_or_week_parser("2020-01-01")
        ymd_mock.assert_called_with("2020-01-01")

    @patch("worklog.parser._calendar_week_parser")
    def test_combined_month_or_day_or_week_parser_cw(self, cw_mock):
        _combined_month_or_day_or_week_parser("2020-W01")
        cw_mock.assert_called_with("2020-W01")

    def test_ym_parser_invalid_value(self):
        with self.assertRaises(ArgumentTypeError):
            _year_month_parser("foobar")

    def test_ym_parser_ym(self):
        expected = datetime(year=2020, month=1, day=1, tzinfo=LOCAL_TIMEZONE)
        actual = _year_month_parser("2020-01")
        self.assertEqual(expected, actual)

    def test_ymd_parser_invalid_value(self):
        with self.assertRaises(ArgumentTypeError):
            _year_month_day_parser("foobar")

    def test_ymd_parser_ymd(self):
        expected = datetime(year=2020, month=1, day=2, tzinfo=LOCAL_TIMEZONE)
        actual = _year_month_day_parser("2020-01-02")
        self.assertEqual(expected, actual)

    def test_cw_parser_invalid_value(self):
        with self.assertRaises(ArgumentTypeError):
            _calendar_week_parser("foobar")

    def test_cw_parser_ymd(self):
        expected = datetime(year=2019, month=12, day=30, tzinfo=LOCAL_TIMEZONE)
        actual = _calendar_week_parser("2020-W00")
        self.assertEqual(expected, actual)
        expected = datetime(year=2020, month=1, day=6, tzinfo=LOCAL_TIMEZONE)
        actual = _calendar_week_parser("2020-W01")
        self.assertEqual(expected, actual)

    @patch("sys.stderr", new_callable=StringIO)
    def test_missing_subcmd_throws_and_exits(self, mock_err):
        with self.assertRaises(SystemExit):
            with self.assertRaises(Exception):
                self.parser.parse_args()

        self.assertIn("invalid choice", mock_err.getvalue())

    def test_subcmd_status(self):
        argv = ["status"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "status")
        self.assertFalse(cli_args.yesterday)
        self.assertIsNone(cli_args.fmt)

    def test_subcmd_status_yesterday(self):
        argv = ["status", "--yesterday"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "status")
        self.assertTrue(cli_args.yesterday)

    def test_subcmd_status_fmt(self):
        argv = ["status", "--fmt", "{position}"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "status")
        self.assertEqual(cli_args.fmt, "{position}")

    def test_subcmd_doctor(self):
        argv = ["doctor"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "doctor")

    def test_subcmd_log(self):
        argv = ["log"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "log")
        self.assertEqual(cli_args.number, 10)
        self.assertFalse(cli_args.all)

    def test_subcmd_log_with_pos_number(self):
        argv = ["log", "-n", "5"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "log")
        self.assertEqual(cli_args.number, 5)

    @patch("sys.stderr", new_callable=StringIO)
    def test_subcmd_log_with_neg_number(self, mock_err):
        argv = ["log", "-n", "-5"]

        with self.assertRaises(SystemExit):
            with self.assertRaises(Exception):
                self.parser.parse_args(argv)

        self.assertIn(
            "argument -n/--number: -5 is not a positive int value", mock_err.getvalue()
        )

    def test_subcmd_log_all(self):
        argv = ["log", "--all"]
        cli_args = self.parser.parse_args(argv)

        self.assertEqual(cli_args.subcmd, "log")
        self.assertTrue(cli_args.all)

