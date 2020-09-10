import unittest
from unittest.mock import patch, Mock, call
import tempfile
from pathlib import Path
import os
import logging

from worklog.log import Log
from worklog.errors import ErrMsg
import worklog.constants as wc


class TestInit(unittest.TestCase):
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
        fp = (
            Path("worklog", "tests", "snapshots", "session_simple.csv")
            .absolute()
            .as_posix()
        )
        instance = Log(fp)
        self.assertFalse(instance._log_df.empty)


class TestDoctor(unittest.TestCase):
    def test_session_only(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = (
                Path("worklog", "tests", "snapshots", "doctor_session_only.csv")
                .absolute()
                .as_posix()
            )
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
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
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-04"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)

    def test_session_with_tasks(self):
        logger = logging.getLogger("test_logger")
        with patch.object(logger, "error") as mock_logger:
            fp = (
                Path("worklog", "tests", "snapshots", "doctor_session_with_tasks.csv")
                .absolute()
                .as_posix()
            )
            instance = Log(fp, logger=logger)
            instance.doctor()

            calls = (
                call(
                    ErrMsg.MISSING_SESSION_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-03"
                    )
                ),
                call(ErrMsg.WRONG_SESSION_ORDER.value.format(date="2020-01-07")),
                call(ErrMsg.WRONG_SESSION_ORDER.value.format(date="2020-01-08")),
                call(
                    ErrMsg.MISSING_TASK_ENTRY.value.format(
                        type=wc.TOKEN_STOP, date="2020-01-04", task_id="task4"
                    )
                ),
                call(
                    ErrMsg.MISSING_TASK_ENTRY.value.format(
                        type=wc.TOKEN_START, date="2020-01-05", task_id="task5"
                    )
                ),
                call(
                    ErrMsg.WRONG_TASK_ORDER.value.format(
                        date="2020-01-06", task_id="task6"
                    )
                ),
                call(
                    ErrMsg.WRONG_TASK_ORDER.value.format(
                        date="2020-01-09", task_id="task9"
                    )
                ),
            )

            mock_logger.assert_has_calls(calls)
