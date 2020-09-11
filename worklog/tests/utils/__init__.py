from pandas import DataFrame
import pandas as pd
from pathlib import Path

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
        Path("worklog", "tests", "data", f"{id}.csv").absolute().as_posix(),
        sep="|",
        header=None,
        names=SCHEMA_COL_NAMES,
        parse_dates=SCHEMA_DATE_COLS,
    )
