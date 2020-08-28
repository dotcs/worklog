import unittest
import numpy as np

from worklog.utils.schema import empty_df_from_schema, get_datetime_cols_from_schema


class TestSchema(unittest.TestCase):
    def test_empty_df(self):
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
