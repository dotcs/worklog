import unittest
import pytest
from unittest.mock import patch, Mock, call
import tempfile
from pathlib import Path
import os
import logging
from datetime import datetime, timezone, date
import snapshottest

from worklog.breaks import AutoBreak
from worklog.log import Log
from worklog.errors import ErrMsg
import worklog.constants as wc


class TestDataMixin(object):
    def _get_testdata_fp(self, name):
        return Path("worklog", "tests", "data", f"{name}.csv").absolute().as_posix()


class CapSysMixin(object):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self._capsys = capsys


class TestInit(unittest.TestCase, TestDataMixin):
    def test_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir, "foobar")
            instance = Log(fp)

            self.assertTrue(fp.exists())

    def test_file_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir, "foobar")
            instance = Log(fp)

            self.assertTrue(os.access(fp, os.R_OK))
            self.assertTrue(os.access(fp, os.W_OK))

    def test_file_is_read(self):
        fp = self._get_testdata_fp("session_simple")
        instance = Log(fp)
        self.assertFalse(instance._log_df.empty)


class TestDoctorSession(unittest.TestCase, TestDataMixin):
    def test_ok(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_session_ok")
            instance = Log(fp, logger=logger)
            instance.doctor()

            mock_logger.assert_not_called()

    def test_stop_entry_missing_single(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_session_stop_missing_single")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-01"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_stop_entry_missing_multiple(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_session_stop_missing_multiple")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-01"
                    )
                ),
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-02"
                    )
                ),
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-03"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_wrong_order(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_session_wrong_order")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (call(ErrMsg.WRONG_SESSION_ORDER.value.format(date="2020-01-01")),)

            mock_logger.assert_has_calls(calls)

    def test_wrong_order_2(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_session_wrong_order_2")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (call(ErrMsg.WRONG_SESSION_ORDER.value.format(date="2020-01-01")),)

            mock_logger.assert_has_calls(calls)


class TestDoctorTask(unittest.TestCase, TestDataMixin):
    def test_ok(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_task_ok")
            instance = Log(fp, logger=logger)
            instance.doctor()

            mock_logger.assert_not_called()

    def test_task_start_entry_missing(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_task_start_missing")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.MISSING_TASK_ENTRY.value.format(
                        type=wc.TOKEN_START, date="2020-01-01", task_id="task1"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_task_stop_entry_missing(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_task_stop_missing")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.MISSING_TASK_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-01", task_id="task1"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_task_wrong_order(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_task_wrong_order")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.WRONG_TASK_ORDER.value.format(
                        date="2020-01-01", task_id="task1"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_task_wrong_order_2(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = self._get_testdata_fp("doctor_task_wrong_order_2")
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.WRONG_TASK_ORDER.value.format(
                        date="2020-01-01", task_id="task1"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)


class TestListTasks(unittest.TestCase, TestDataMixin):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self._capsys = capsys

    def test_list_tasks(self):
        fp = self._get_testdata_fp("tasks_multiple_nested")
        instance = Log(fp)
        instance.list_tasks()

        out, err = self._capsys.readouterr()
        expected = """These tasks are listed in the log:
task1 (2)
task2 (2)
task3 (2)
"""
        assert out == expected


class TestReport(snapshottest.TestCase, TestDataMixin, CapSysMixin):
    def test_report_with_tasks(self):
        fp = self._get_testdata_fp("report_with_tasks")
        instance = Log(fp)
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2020, 3, 1, tzinfo=timezone.utc)
        instance.report(date_from, date_to)

        out, _ = self._capsys.readouterr()
        self.assertMatchSnapshot(out)

    def test_report_with_tasks_and_autobreak(self):
        fp = self._get_testdata_fp("report_with_tasks")
        instance = Log(fp)
        instance.auto_break = AutoBreak(limits=[0], durations=[60])
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2020, 3, 1, tzinfo=timezone.utc)
        instance.report(date_from, date_to)

        out, _ = self._capsys.readouterr()
        self.assertMatchSnapshot(out)


class TestStatus(snapshottest.TestCase, TestDataMixin, CapSysMixin):
    def test_empty(self):
        fp = self._get_testdata_fp("status_empty")
        instance = Log(fp)
        query_date = date(2020, 1, 1)

        with self.assertRaises(SystemExit) as err:
            instance.status(8, 10, query_date=query_date)

        _, stderr = self._capsys.readouterr()
        self.assertEqual(
            stderr, ErrMsg.EMPTY_LOG_DATA.value + "\n",
        )

        self.assertEqual(err.exception.code, 1)

    def test_empty_with_fmt(self):
        fp = self._get_testdata_fp("status_empty")
        instance = Log(fp)
        query_date = date(2020, 1, 1)

        with self.assertRaises(SystemExit) as err:
            instance.status(8, 10, query_date=query_date, fmt="{tracking_status}")

        out, _ = self._capsys.readouterr()
        self.assertEqual(out, ErrMsg.NA.value)

        self.assertEqual(err.exception.code, 0)

    def test_tracking_on(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_on")
            instance = Log(fp)
            query_date = date(2020, 1, 1)

            instance.status(8, 10, query_date=query_date)

        out, _ = self._capsys.readouterr()
        self.assertMatchSnapshot(out)

    def test_tracking_on_with_fmt(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_on")
            instance = Log(fp)
            query_date = date(2020, 1, 1)

            instance.status(8, 10, query_date=query_date, fmt="{tracking_status}")

        out, _ = self._capsys.readouterr()
        self.assertEqual(out, "on")

    def test_tracking_off(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_off")
            instance = Log(fp)
            query_date = date(2020, 1, 1)

            instance.status(8, 10, query_date=query_date)

        out, _ = self._capsys.readouterr()
        self.assertMatchSnapshot(out)

    def test_tracking_off_with_fmt(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_off")
            instance = Log(fp)
            query_date = date(2020, 1, 1)

            instance.status(8, 10, query_date=query_date, fmt="{tracking_status}")

        out, _ = self._capsys.readouterr()
        self.assertEqual(out, "off")

    def test_day_with_no_content(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_off")
            instance = Log(fp)
            query_date = date(2020, 1, 2)

            with self.assertRaises(SystemExit) as err:
                instance.status(8, 10, query_date=query_date)

        _, stderr = self._capsys.readouterr()
        self.assertEqual(
            stderr,
            ErrMsg.EMPTY_LOG_DATA_FOR_DATE.value.format(query_date=query_date) + "\n",
        )
        self.assertEqual(err.exception.code, 1)

    def test_day_with_no_content_fmt(self):
        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            fp = self._get_testdata_fp("status_tracking_off")
            instance = Log(fp)
            query_date = date(2020, 1, 2)

            with self.assertRaises(SystemExit) as err:
                instance.status(8, 10, query_date=query_date, fmt="{tracking_status}")

        stdout, _ = self._capsys.readouterr()
        self.assertEqual(stdout, ErrMsg.NA.value)
        self.assertEqual(err.exception.code, 0)


class TestCommit(snapshottest.TestCase, TestDataMixin, CapSysMixin):
    def test_invalid_type(self):
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            with self.assertRaises(ValueError):
                instance.commit(wc.TOKEN_SESSION, "foobar")

    def test_invalid_category(self):
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            with self.assertRaises(ValueError):
                instance.commit("foobar", wc.TOKEN_START)

    @patch("worklog.log.now_localtz")
    def test_session_start(self, mock_now):
        mock_now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_START, time="2020-01-01T00:00:00+00:00"
            )

            fh.seek(0)

            content = fh.read().decode()
            self.assertMatchSnapshot(content)

    @patch("worklog.log.now_localtz")
    def test_session_start_and_stop(self, mock_now):
        mock_now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_START, time="2020-01-01T00:00:00+00:00"
            )
            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_STOP, time="2020-01-01T01:00:00+00:00"
            )

            fh.seek(0)

            content = fh.read().decode()
            self.assertMatchSnapshot(content)

    @patch("worklog.log.now_localtz")
    def test_session_and_task(self, mock_now):
        mock_now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_START, time="2020-01-01T00:00:00+00:00"
            )
            instance.commit(
                wc.TOKEN_TASK,
                wc.TOKEN_START,
                time="2020-01-01T00:00:00+00:00",
                identifier="task1",
            )
            instance.commit(
                wc.TOKEN_TASK,
                wc.TOKEN_STOP,
                time="2020-01-01T01:00:00+00:00",
                identifier="task1",
            )
            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_STOP, time="2020-01-01T01:00:00+00:00",
            )

            fh.seek(0)

            content = fh.read().decode()
            self.assertMatchSnapshot(content)

    @patch("worklog.log.now_localtz")
    def test_stop_session_with_running_task(self, mock_now):
        mock_now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_START, time="2020-01-01T00:00:00+00:00"
            )
            instance.commit(
                wc.TOKEN_TASK,
                wc.TOKEN_START,
                time="2020-01-01T00:00:00+00:00",
                identifier="task1",
            )

            with self.assertRaises(SystemExit) as err:
                instance.commit(
                    wc.TOKEN_SESSION, wc.TOKEN_STOP, time="2020-01-01T01:00:00+00:00",
                )

            _, stderr = self._capsys.readouterr()

            self.assertEqual(
                stderr,
                ErrMsg.STOP_SESSION_TASKS_RUNNING.value.format(active_tasks=["task1"])
                + "\n",
            )
            self.assertTrue(err.exception.code, 1)

    @patch("worklog.log.now_localtz")
    def test_stop_session_with_running_task_force(self, mock_now):
        mock_now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        with tempfile.NamedTemporaryFile() as fh:
            instance = Log(fh.name)

            instance.commit(
                wc.TOKEN_SESSION, wc.TOKEN_START, time="2020-01-01T00:00:00+00:00"
            )
            instance.commit(
                wc.TOKEN_TASK,
                wc.TOKEN_START,
                time="2020-01-01T00:00:00+00:00",
                identifier="task1",
            )
            instance.commit(
                wc.TOKEN_SESSION,
                wc.TOKEN_STOP,
                time="2020-01-01T01:00:00+00:00",
                force=True,
            )

            fh.seek(0)

            content = fh.read().decode()
            self.assertMatchSnapshot(content)
