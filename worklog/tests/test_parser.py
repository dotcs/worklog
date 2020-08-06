import unittest
from unittest.mock import patch
from io import StringIO
from argparse import ArgumentParser, ArgumentError, ArgumentTypeError

from worklog.parser import get_arg_parser, _positive_int


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

