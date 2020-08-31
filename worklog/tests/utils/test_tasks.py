import unittest
from unittest.mock import Mock
import pandas as pd
from pandas import DataFrame
from datetime import datetime, date, timedelta, timezone
import logging

import worklog.constants as wc
from worklog.tests.utils import read_log_sample, SCHEMA
from worklog.utils.schema import empty_df_from_schema
from worklog.utils.tasks import (
    _calc_single_task_duration,
    calc_task_durations,
    extract_intervals,
    get_active_task_ids,
    get_all_task_ids_with_duration,
)


class TestTaskIds(unittest.TestCase):
    def test_get_all_task_ids_with_duration_empty(self):
        df = empty_df_from_schema(SCHEMA)
        expected = {}
        actual = get_all_task_ids_with_duration(df)
        self.assertEqual(actual, expected)

    def test_get_all_task_ids_with_duration(self):
        df = read_log_sample("tasks_multiple_nested")
        expected = {
            "task1": timedelta(hours=2),
            "task2": timedelta(minutes=1),
            "task3": timedelta(hours=1, minutes=30),
        }
        actual = get_all_task_ids_with_duration(df)
        self.assertEqual(actual, expected)

    def test_get_active_task_ids_empty(self):
        df = empty_df_from_schema(SCHEMA)
        expected = []
        actual = get_active_task_ids(df)
        self.assertEqual(actual, expected)

    def test_get_active_task_ids_single(self):
        df = read_log_sample("tasks_simple_active")
        expected = ["task1"]
        actual = get_active_task_ids(df)
        self.assertEqual(actual, expected)

    def test_get_active_task_ids_multiple(self):
        df = read_log_sample("tasks_multiple_started")
        expected = ["task1", "task3"]
        actual = get_active_task_ids(df)
        self.assertEqual(actual, expected)


class TestTaskIntervals(unittest.TestCase):
    def test_extract_intervals_empty_dataframe(self):
        df = DataFrame()

        actual = extract_intervals(df)
        expected = DataFrame(columns=["date", "start", "stop", "interval"])

        pd.testing.assert_frame_equal(actual, expected)

    def test_extract_intervals_valid(self):
        mock_logger = Mock(logging.Logger)
        df = read_log_sample("tasks_simple_ordered")

        actual = extract_intervals(df, logger=mock_logger)
        expected = DataFrame(
            {
                "date": [date(2020, 1, 1)],
                "start": [datetime(2020, 1, 1, 0, tzinfo=timezone.utc)],
                "stop": [datetime(2020, 1, 1, 1, tzinfo=timezone.utc)],
                "interval": [timedelta(hours=1)],
            }
        )

        pd.testing.assert_frame_equal(actual, expected)
        mock_logger.error.assert_not_called()

    def test_extract_intervals_invalid_start_missing(self):
        mock_logger = Mock(logging.Logger)
        df = read_log_sample("tasks_start_missing")

        actual = extract_intervals(df, logger=mock_logger)
        expected = DataFrame(columns=["date", "start", "stop", "interval"])

        pd.testing.assert_frame_equal(actual, expected)
        mock_logger.error.assert_called_once_with("No start entry found. Skip entry.")

    def test_extract_intervals_invalid_stop_missing(self):
        mock_logger = Mock(logging.Logger)
        df = read_log_sample("tasks_open_interval")

        actual = extract_intervals(df, logger=mock_logger)
        expected = DataFrame(
            {
                "date": [date(2020, 1, 1)],
                "start": [datetime(2020, 1, 1, 0, tzinfo=timezone.utc)],
                "stop": [datetime(2020, 1, 1, 1, tzinfo=timezone.utc)],
                "interval": [timedelta(hours=1)],
            }
        )

        pd.testing.assert_frame_equal(actual, expected)
        mock_logger.error.assert_called_once_with(
            "Start entry at 2020-01-01 01:30:00+00:00 has no stop entry. Skip entry."
        )

    def test_extract_intervals_invalid_unknown_type(self):
        mock_logger = Mock(logging.Logger)
        df = read_log_sample("tasks_invalid_type")

        actual = extract_intervals(df, logger=mock_logger)
        expected = DataFrame(
            {
                "date": [date(2020, 1, 1)],
                "start": [datetime(2020, 1, 1, 0, tzinfo=timezone.utc)],
                "stop": [datetime(2020, 1, 1, 1, tzinfo=timezone.utc)],
                "interval": [timedelta(hours=1)],
            }
        )

        pd.testing.assert_frame_equal(actual, expected)
        mock_logger.error.assert_called_once_with(
            "Found unknown type 'unknown'. Skip entry."
        )


class TestTaskDuration(unittest.TestCase):
    def test_calc_task_durations_ordered(self):
        df = read_log_sample("tasks_simple_ordered")
        expected = DataFrame(
            {wc.COL_TASK_IDENTIFIER: ["foo"], "time": [timedelta(hours=1)]}, index=[1]
        )
        actual = _calc_single_task_duration(
            df, keep_cols=[wc.COL_TASK_IDENTIFIER, "time"]
        )
        pd.testing.assert_frame_equal(actual, expected)

    def test_calc_task_durations_open_interval(self):
        df = read_log_sample("tasks_open_interval")
        expected = DataFrame(
            {wc.COL_TASK_IDENTIFIER: ["foo"], "time": [timedelta(hours=1)]}, index=[1]
        )
        actual = _calc_single_task_duration(
            df, keep_cols=[wc.COL_TASK_IDENTIFIER, "time"]
        )
        pd.testing.assert_frame_equal(actual, expected)

    def calc_task_durations_multiple_ordered(self):
        df = read_log_sample("tasks_multiple_ordered")
        expected = DataFrame(
            {
                wc.COL_TASK_IDENTIFIER: ["bar", "foo"],
                "time": [timedelta(minutes=30), timedelta(hours=1)],
            },
            index=[3, 1],
        )
        actual = calc_task_durations(df)
        pd.testing.assert_frame_equal(actual, expected)

    def test_calc_task_durations_multiple_nested(self):
        """
        Test if the implementation works if tasks are nested.
        """
        df = read_log_sample("tasks_multiple_nested")
        expected = DataFrame(
            {
                wc.COL_TASK_IDENTIFIER: ["task1", "task2", "task3"],
                "time": [
                    timedelta(hours=2),
                    timedelta(minutes=1),
                    timedelta(hours=1, minutes=30),
                ],
            },
            index=pd.MultiIndex.from_tuples(
                [("task1", 4), ("task2", 3), ("task3", 5)],
                names=[wc.COL_TASK_IDENTIFIER, None],
            ),
        )
        actual = calc_task_durations(df)
        pd.testing.assert_frame_equal(actual, expected)

    def test_calc_task_durations_multiple_unordered(self):
        """
        Test if implementation works if the log entries are in the wrong
        order. In this case a stop entry is listed before a start entry
        although the order of the logged time is fine.
        """
        df = read_log_sample("tasks_multiple_nested_unordered")
        expected = DataFrame(
            {
                wc.COL_TASK_IDENTIFIER: ["task1", "task2"],
                "time": [timedelta(hours=2), timedelta(minutes=1)],
            },
            index=pd.MultiIndex.from_tuples(
                [("task1", 1), ("task2", 0)], names=[wc.COL_TASK_IDENTIFIER, None],
            ),
        )
        actual = calc_task_durations(df)
        pd.testing.assert_frame_equal(actual, expected)
