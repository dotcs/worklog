from typing import Optional
import unittest
import logging
from unittest.mock import patch, Mock
from io import StringIO
from datetime import timedelta
import pandas as pd
from pandas import DataFrame, Series  # type: ignore
from datetime import datetime, date, timezone
import numpy as np  # type: ignore
import sys
from pathlib import Path

import worklog.constants as wc
from worklog.utils import (
    _calc_single_task_duration,
    _get_or_update_dt,
    calc_log_time,
    calc_task_durations,
    check_order_session,
    configure_logger,
    empty_df_from_schema,
    extract_intervals,
    format_numpy_timedelta,
    format_timedelta,
    get_active_task_ids,
    get_all_task_ids_with_duration,
    get_datetime_cols_from_schema,
    get_pager,
    sentinel_datetime,
)

SCHEMA = [
    (wc.COL_COMMIT_DATETIME, "datetime64[ns]",),
    (wc.COL_LOG_DATETIME, "datetime64[ns]",),
    (wc.COL_CATEGORY, "object",),
    (wc.COL_TYPE, "object",),
    (wc.COL_TASK_IDENTIFIER, "object",),
]

SCHEMA_COL_NAMES = [col for col, _ in SCHEMA]
SCHEMA_DATE_COLS = [wc.COL_COMMIT_DATETIME, wc.COL_LOG_DATETIME]


def read_log_sample(id: str) -> DataFrame:
    return pd.read_csv(
        f"worklog/tests/snapshots/{id}.csv",
        sep="|",
        header=None,
        names=SCHEMA_COL_NAMES,
        parse_dates=SCHEMA_DATE_COLS,
    )


class TestUtils(unittest.TestCase):
    def test_format_timedelta_invalid_value(self):
        td = None
        expected = "00:00:00"
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_format_timedelta(self):
        td = timedelta(hours=1, minutes=5, seconds=30)
        expected = "01:05:30"
        actual = format_timedelta(td)
        self.assertEqual(expected, actual)

    def test_empty_df_from_schema(self):
        schema = [
            ("commit_dt", "datetime64[ns]",),
            ("log_dt", "datetime64[ns]",),
            ("category", "object",),
            ("type", "object",),
        ]

        df = empty_df_from_schema(schema)
        self.assertListEqual(
            df.dtypes.values.tolist(),
            [np.dtype("<M8[ns]"), np.dtype("<M8[ns]"), np.dtype("O"), np.dtype("O")],
        )
        self.assertTupleEqual(df.shape, (0, len(schema)))

    def test_get_datetime_cols_from_schema(self):
        schema = [
            ("commit_dt", "datetime64[ns]",),
            ("log_dt", "datetime64[ns]",),
            ("category", "object",),
            ("type", "object",),
        ]

        actual = get_datetime_cols_from_schema(schema)
        self.assertListEqual(["commit_dt", "log_dt"], actual)

    def test_check_order_session(self):
        schema = [
            ("log_dt", "datetime64[ns]",),
            ("category", "object",),
            ("type", "object",),
        ]

        rows = [
            {
                "log_dt": datetime(2020, 1, 1, 0, 0, 0, 0, timezone.utc),
                "category": "session",
                "type": "start",
            },
            {
                "log_dt": datetime(2020, 1, 1, 1, 0, 0, 0, timezone.utc),
                "category": "session",
                "type": "stop",
            },
            {
                "log_dt": datetime(2020, 1, 1, 2, 0, 0, 0, timezone.utc),
                "category": "session",
                "type": "stop",
            },
        ]

        logger = logging.getLogger("test_check_order_session")
        df = empty_df_from_schema(schema)

        # Positive case
        df1 = df.append(rows[:2], ignore_index=True)
        df1["date"] = df1["log_dt"].apply(lambda x: x.date())
        df1["time"] = df1["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df1, logger)
            mock_error.assert_not_called()

        # Two stop entries after each other -> Error!
        df2 = df.append(rows[:3], ignore_index=True)
        df2["date"] = df2["log_dt"].apply(lambda x: x.date())
        df2["time"] = df2["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df2, logger)
            mock_error.assert_called_with(
                '"session" entries on date 2020-01-01 are not ordered correctly.'
            )

        # First entry is a 'stop' entry -> Error!
        df3 = df.append(rows[1:2], ignore_index=True)
        df3["date"] = df3["log_dt"].apply(lambda x: x.date())
        df3["time"] = df3["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df3, logger)
            mock_error.assert_called_with(
                'First entry of type "session" on date 2020-01-01 is not "start".'
            )

        # Last entry is 'start' and 'stop' entry is missing -> Error!
        df4 = df.append(rows[0:1], ignore_index=True)
        df4["date"] = df4["log_dt"].apply(lambda x: x.date())
        df4["time"] = df4["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df4, logger)
            mock_error.assert_called_with("Date 2020-01-01 has no stop entry.")

    @patch("worklog.utils.datetime")
    def test_sentinel_datetime(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 1, 2, 1, 33, 7, 0, timezone.utc)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Date is in the past -> Sentinal value is last second on this date
        target_date1 = date(2019, 1, 1)
        actual_1 = sentinel_datetime(target_date1, tzinfo=timezone.utc)
        self.assertEqual(actual_1.isoformat(), "2019-01-01T23:59:59+00:00")

        # Date is on the same day as today -> Sentinel value is datetime.now()
        target_date2 = date(2020, 1, 2)
        actual_2 = sentinel_datetime(target_date2, tzinfo=timezone.utc)
        self.assertEqual(actual_2.isoformat(), "2020-01-02T01:33:07+00:00")

        # Date is yesterday -> Sentinel value is the last second on this date
        target_date3 = date(2020, 1, 1)
        actual_3 = sentinel_datetime(target_date3, tzinfo=timezone.utc)
        self.assertEqual(actual_3.isoformat(), "2020-01-01T23:59:59+00:00")

        # Date is in the future -> Raise error
        with self.assertRaises(ValueError):
            target_date4 = date(2020, 1, 3)
            sentinel_datetime(target_date4, tzinfo=timezone.utc)

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

    def test_get_all_task_ids_with_duration(self):
        df = read_log_sample("tasks_multiple_nested")
        expected = {
            "task1": timedelta(hours=2),
            "task2": timedelta(minutes=1),
            "task3": timedelta(hours=1, minutes=30),
        }
        actual = get_all_task_ids_with_duration(df)
        self.assertEqual(actual, expected)

    def test_get_active_task_ids(self):
        df = read_log_sample("tasks_simple_active")
        expected = ["task1"]
        actual = get_active_task_ids(df)
        self.assertEqual(actual, expected)

    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_no_less_and_env_unset(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", None]
        mock_getenv.side_effect = lambda _, default_value: default_value

        actual = get_pager()
        expected = "/path/to/more"

        self.assertEqual(actual, expected)

    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_no_less_and_env_set(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", None]
        mock_getenv.return_value = "/path/to/less"

        actual = get_pager()
        expected = "/path/to/less"

        self.assertEqual(actual, expected)

    @patch("os.getenv")
    @patch("shutil.which")
    def test_get_pager_has_less_and_env_unset(self, mock_which, mock_getenv):
        mock_which.side_effect = ["/path/to/more", "/path/to/less"]
        mock_getenv.side_effect = lambda _, default_value: default_value

        actual = get_pager()
        expected = "/path/to/less"

        self.assertEqual(actual, expected)

    def test_get_or_update_dt_with_time(self):
        dt = datetime(2020, 1, 1, 0, 0, 0, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "05:06")
        expected = datetime(2020, 1, 1, 5, 6, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "14:06")
        expected = datetime(2020, 1, 1, 14, 6, tzinfo=wc.LOCAL_TIMEZONE)

        self.assertEqual(actual, expected)

    def test_get_or_update_dt_with_iso_datestr(self):
        dt = datetime(2020, 1, 1, 0, 0, 0, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "1999-12-13")
        expected = datetime(1999, 12, 13, 0, 0, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "1999-12-13T01:12")
        expected = datetime(1999, 12, 13, 1, 12, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "2020-02-03 04:05")
        expected = datetime(2020, 2, 3, 4, 5, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "2020-02-03 14:05:03")
        expected = datetime(2020, 2, 3, 14, 5, tzinfo=wc.LOCAL_TIMEZONE)

        actual = _get_or_update_dt(dt, "2020-02-03 04:05:03+00:00")
        expected = datetime(2020, 2, 3, 4, 5, tzinfo=timezone.utc)

        self.assertEqual(actual, expected)

    @patch(
        "worklog.utils.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    def test_calc_log_time_no_corrections(self):

        expected = datetime(2020, 1, 1, tzinfo=timezone.utc)
        actual = calc_log_time()

        self.assertEqual(actual, expected)

    @patch(
        "worklog.utils.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    @patch("worklog.utils._get_or_update_dt")
    def test_calc_log_time_with_time_corrections(self, mock):

        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        actual = calc_log_time(time="20:21")

        mock.assert_called_with(dt, "20:21")

    @patch(
        "worklog.utils.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    @patch("worklog.utils._get_or_update_dt")
    def test_calc_log_time_with_offset_minutes_corrections(self, mock):

        expected = datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc)
        actual = calc_log_time(offset_min=10)

        mock.assert_not_called()
        self.assertEqual(actual, expected)

    def test_format_numpy_timedelta_nat(self):
        actual = format_numpy_timedelta(np.timedelta64("nAt"))
        expected = "00:00:00"

        self.assertEqual(actual, expected)

    def test_format_numpy_timedelta_valid(self):
        actual = format_numpy_timedelta(np.timedelta64(100, "s"))
        expected = "00:01:40"

        self.assertEqual(actual, expected)

    def test_format_numpy_timedelta_valid_days(self):
        actual = format_numpy_timedelta(np.timedelta64(2, "D"))
        expected = "48:00:00"

        self.assertEqual(actual, expected)

        actual = format_numpy_timedelta(np.timedelta64(20, "D"))
        expected = "480:00:00"

        self.assertEqual(actual, expected)

    def test_configure_logger_name(self):
        logger = configure_logger()
        name = logger.name
        self.assertEqual(name, wc.DEFAULT_LOGGER_NAME)

    def test_configure_logger_handlers(self):
        logger = configure_logger()

        has_handlers = logger.hasHandlers()
        self.assertTrue(has_handlers)

        sys_handler = logger.handlers[0]
        self.assertEqual(sys_handler.stream, sys.stdout)

    def test_configure_logger_default_log_level(self):
        logger = configure_logger()
        log_level = logger.level
        self.assertEqual(log_level, logging.INFO)

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
        mock_logger.error.assert_called_once()
