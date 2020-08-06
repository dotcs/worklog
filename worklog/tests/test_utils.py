from typing import Optional
import unittest
import logging
from unittest.mock import patch
from io import StringIO
from datetime import timedelta
from pandas import DataFrame, Series  # type: ignore
from datetime import datetime, date, timezone
import numpy as np  # type: ignore

from worklog.utils import (
    format_timedelta,
    empty_df_from_schema,
    get_datetime_cols_from_schema,
    check_order_session,
    sentinel_datetime,
)


class TestUtils(unittest.TestCase):
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
