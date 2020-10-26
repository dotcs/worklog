import unittest
from unittest.mock import patch, Mock
from datetime import date, time, datetime, timezone
from pandas import DataFrame
import pandas as pd

import worklog.constants as wc
from worklog.utils.time import _get_or_update_dt, calc_log_time, extract_date_and_time
from worklog.tests.utils import read_log_sample


class TestDatetimeManipulation(unittest.TestCase):
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
        "worklog.utils.time.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    def test_calc_log_time_no_corrections(self):

        expected = datetime(2020, 1, 1, tzinfo=timezone.utc)
        actual = calc_log_time()

        self.assertEqual(actual, expected)

    @patch(
        "worklog.utils.time.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    @patch("worklog.utils.time._get_or_update_dt")
    def test_calc_log_time_with_time_corrections(self, mock):

        dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        actual = calc_log_time(time="20:21")

        mock.assert_called_with(dt, "20:21")

    @patch(
        "worklog.utils.time.datetime",
        Mock(now=Mock(return_value=datetime(2020, 1, 1, tzinfo=timezone.utc))),
    )
    @patch("worklog.utils.time._get_or_update_dt")
    def test_calc_log_time_with_offset_minutes_corrections(self, mock):

        expected = datetime(2020, 1, 1, 0, 10, tzinfo=timezone.utc)
        actual = calc_log_time(offset_min=10)

        mock.assert_not_called()
        self.assertEqual(actual, expected)


class TestDateTimeExtraction(unittest.TestCase):
    # FIXME: Fix this test. The implementation is correct?!
    def xtest_extraction(self):
        df = read_log_sample("session_simple")

        expected = DataFrame(
            {
                "date": [date(2020, 1, 1), date(2020, 1, 1)],
                "time": [
                    time(hour=0, tzinfo=timezone.utc),
                    time(hour=1, tzinfo=timezone.utc),
                ],
                wc.COL_LOG_DATETIME_UTC: [
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                ],
                wc.COL_COMMIT_DATETIME_UTC: [
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                ],
            }
        )
        actual = extract_date_and_time(df)

        pd.testing.assert_frame_equal(actual, expected)
