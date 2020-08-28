from pandas import DataFrame
import pandas as pd

import worklog.constants as wc

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
