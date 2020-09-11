import unittest
import pytest
from unittest.mock import patch, Mock, call
import tempfile
from pathlib import Path
import os
import logging
from datetime import datetime, timezone
import snapshottest

from worklog.breaks import AutoBreak
from worklog.log import Log
from worklog.errors import ErrMsg
import worklog.constants as wc


class TestDataMixin(object):
    def _get_testdata_fp(self, name):
        return Path("worklog", "tests", "data", f"{name}.csv").absolute().as_posix()


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


class TestReport(snapshottest.TestCase, TestDataMixin):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self._capsys = capsys

    def test_report_with_tasks(self):
        fp = self._get_testdata_fp("report_with_tasks")
        instance = Log(fp)
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2020, 3, 1, tzinfo=timezone.utc)
        instance.report(date_from, date_to)

        out, err = self._capsys.readouterr()
        self.assertMatchSnapshot(out)

    def test_report_with_tasks_and_autobreak(self):
        fp = self._get_testdata_fp("report_with_tasks")
        instance = Log(fp)
        instance.auto_break = AutoBreak(limits=[0], durations=[60])
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2020, 3, 1, tzinfo=timezone.utc)
        instance.report(date_from, date_to)

        out, err = self._capsys.readouterr()
        self.assertMatchSnapshot(out)
