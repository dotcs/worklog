import unittest
from unittest.mock import patch
from argparse import ArgumentError, Namespace
from datetime import datetime, timezone, timedelta, date

import worklog.constants as wc
from worklog.dispatcher import dispatch


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchSession(unittest.TestCase):
    def test_invalid(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session",
            type="invalid_value",
            offset_minutes=0,
            time=None,
            force=False,
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_not_called()

    def test_start(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session", type="start", offset_minutes=0, time=None, force=False
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_called_once_with(
            "session", "start", 0, None, force=False
        )

    def test_stop(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session", type="stop", offset_minutes=0, time=None, force=False
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_called_once_with("session", "stop", 0, None, force=False)

    def test_start_with_offset(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session", type="stop", offset_minutes=-11, time=None, force=False
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_called_once_with(
            "session", "stop", -11, None, force=False
        )

    def test_start_with_time(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session",
            type="stop",
            offset_minutes=0,
            time=datetime(2020, 1, 1, tzinfo=timezone.utc),
            force=False,
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_called_once_with(
            "session", "stop", 0, datetime(2020, 1, 1, tzinfo=timezone.utc), force=False
        )

    def test_start_forced(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(
            subcmd="session", type="stop", offset_minutes=0, time=None, force=True,
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.commit.assert_called_once_with("session", "stop", 0, None, force=True)


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchTask(unittest.TestCase):
    def test_start(self, mock_log, mock_parser, mock_cfg):
        """It should be possible to start a new task"""
        ns = Namespace(
            subcmd="task",
            type="start",
            auto_stop=False,
            offset_minutes=0,
            time=None,
            id="foobar",
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.stop_active_tasks.assert_not_called()
        mock_log.commit.assert_called_once_with(
            "task", "start", 0, None, identifier="foobar"
        )

    def test_stop(self, mock_log, mock_parser, mock_cfg):
        """It should be possible to stop a task"""
        ns = Namespace(
            subcmd="task",
            type="stop",
            auto_stop=False,
            offset_minutes=0,
            time=None,
            id="foobar",
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.stop_active_tasks.assert_not_called()
        mock_log.commit.assert_called_once_with(
            "task", "stop", 0, None, identifier="foobar"
        )

    def test_start_with_auto_stop(self, mock_log, mock_parser, mock_cfg):
        """
        It should be possible to start a new task and auto stop all
        currently runnning tasks.
        """
        ns = Namespace(
            subcmd="task",
            type="start",
            auto_stop=True,
            offset_minutes=0,
            time=None,
            id="foobar",
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.stop_active_tasks.assert_called_once()
        mock_log.commit.assert_called_once_with(
            "task", "start", 0, None, identifier="foobar"
        )

    def test_list_tasks(self, mock_log, mock_parser, mock_cfg):
        """It should be possible to list tasks."""
        ns = Namespace(subcmd="task", type="list")
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.list_tasks.assert_called_once()

    def test_report_task_by_id(self, mock_log, mock_parser, mock_cfg):
        """It should be possible to report infos about a single task id."""
        ns = Namespace(subcmd="task", type="report", id="foobar")
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.task_report.assert_called_once_with("foobar")


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchDoctor(unittest.TestCase):
    def test_doctor(self, mock_log, mock_parser, mock_cfg):
        ns = Namespace(subcmd="doctor")
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.doctor.assert_called_once()


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchReport(unittest.TestCase):
    def test_report(self, mock_log, mock_parser, mock_cfg):
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2020, 1, 2, tzinfo=timezone.utc)
        ns = Namespace(subcmd="report", date_from=date_from, date_to=date_to)
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.report.assert_called_once_with(date_from, date_to)


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchStatus(unittest.TestCase):
    def test_status(self, mock_log, mock_parser, mock_cfg):
        mock_cfg.get.side_effect = ["8.0", "10.0"]
        ns = Namespace(subcmd="status", fmt=None, yesterday=False, date=None)
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        expected_query_date = datetime.today().date()

        mock_log.status.assert_called_once_with(
            8.0, 10.0, fmt=None, query_date=expected_query_date
        )

    def test_status_yesterday(self, mock_log, mock_parser, mock_cfg):
        mock_cfg.get.side_effect = ["8.0", "10.0"]
        ns = Namespace(subcmd="status", fmt=None, yesterday=True, date=None)
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        expected_query_date = datetime.today().date() - timedelta(days=1)

        mock_log.status.assert_called_once_with(
            8.0, 10.0, fmt=None, query_date=expected_query_date
        )

    def test_status_fixed_date(self, mock_log, mock_parser, mock_cfg):
        mock_cfg.get.side_effect = ["8.0", "10.0"]
        ns = Namespace(
            subcmd="status",
            fmt=None,
            yesterday=False,
            date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        expected_query_date = date(2020, 1, 1)

        mock_log.status.assert_called_once_with(
            8.0, 10.0, fmt=None, query_date=expected_query_date
        )


@patch("configparser.ConfigParser")
@patch("argparse.ArgumentParser")
@patch("worklog.log")
class TestDispatchLog(unittest.TestCase):
    def test_log_default(self, mock_log, mock_parser, mock_cfg):
        mock_cfg.get.side_effect = ["10"]  # worklog.no_pager_max_entries
        ns = Namespace(subcmd="log", no_pager=False, all=False, category=None, number=5)
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.log.assert_called_once_with(5, False, None)

    def test_log_all(self, mock_log, mock_parser, mock_cfg):
        mock_cfg.get.side_effect = ["10"]  # worklog.no_pager_max_entries
        ns = Namespace(subcmd="log", no_pager=False, all=True, category=None, number=5)
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.log.assert_called_once_with(-1, True, None)

    def test_log_large_n(self, mock_log, mock_parser, mock_cfg):
        """It should automatically use pager if number > no_pager_max_entries"""
        mock_cfg.get.side_effect = ["10"]  # worklog.no_pager_max_entries
        ns = Namespace(
            subcmd="log", no_pager=False, all=False, category=None, number=20
        )
        dispatch(mock_log, mock_parser, ns, mock_cfg)

        mock_log.log.assert_called_once_with(20, True, None)
