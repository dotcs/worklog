import unittest
from unittest.mock import patch
import logging
from datetime import datetime, date, timezone

from worklog.utils.schema import empty_df_from_schema
import worklog.constants as wc
from worklog.utils.session import (
    check_order_session,
    sentinel_datetime,
    is_active_session,
)
from worklog.errors import ErrMsg
from worklog.tests.utils import read_log_sample


class TestSessionOrder(unittest.TestCase):
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
                ErrMsg.MISSING_SESSION_ENTRY.value.format(
                    type=wc.TOKEN_START, date="2020-01-01"
                )
            )

        # First entry is a 'stop' entry -> Error!
        df3 = df.append(rows[1:2], ignore_index=True)
        df3["date"] = df3["log_dt"].apply(lambda x: x.date())
        df3["time"] = df3["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df3, logger)
            mock_error.assert_called_with(
                ErrMsg.MISSING_SESSION_ENTRY.value.format(
                    type=wc.TOKEN_START, date="2020-01-01"
                )
            )

        # Last entry is 'start' and 'stop' entry is missing -> Error!
        df4 = df.append(rows[0:1], ignore_index=True)
        df4["date"] = df4["log_dt"].apply(lambda x: x.date())
        df4["time"] = df4["log_dt"].apply(lambda x: x.time())
        with patch.object(logger, "error") as mock_error:
            check_order_session(df4, logger)
            mock_error.assert_called_with(
                ErrMsg.MISSING_SESSION_ENTRY.value.format(
                    type=wc.TOKEN_STOP, date="2020-01-01"
                )
            )


class TestSentinelEntries(unittest.TestCase):
    @patch("worklog.utils.session.datetime")
    def test_sentinel_datetime(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2020, 1, 2, 1, 33, 7, 0, timezone.utc)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        with patch("worklog.constants.LOCAL_TIMEZONE", new=timezone.utc):
            # Date is in the past -> Sentinal value is last second on this date
            target_date1 = date(2019, 1, 1)
            actual_1 = sentinel_datetime(target_date1)
            self.assertEqual(actual_1.isoformat(), "2019-01-01T23:59:59+00:00")

            # Date is on the same day as today -> Sentinel value is datetime.now()
            target_date2 = date(2020, 1, 2)
            actual_2 = sentinel_datetime(target_date2)
            self.assertEqual(actual_2.isoformat(), "2020-01-02T01:33:07+00:00")

            # Date is yesterday -> Sentinel value is the last second on this date
            target_date3 = date(2020, 1, 1)
            actual_3 = sentinel_datetime(target_date3)
            self.assertEqual(actual_3.isoformat(), "2020-01-01T23:59:59+00:00")

            # Date is in the future -> Raise error
            with self.assertRaises(ValueError):
                target_date4 = date(2020, 1, 3)
                sentinel_datetime(target_date4)


class TestSessionActivity(unittest.TestCase):
    def test_inactive_session(self):
        df = read_log_sample("session_simple")
        actual = is_active_session(df)

        self.assertFalse(actual)

    def test_active_session(self):
        df = read_log_sample("session_simple_open")
        actual = is_active_session(df)

        self.assertTrue(actual)
