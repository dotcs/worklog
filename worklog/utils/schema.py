from typing import Iterable, Tuple, Dict, List
from pandas import DataFrame, Series
from functools import reduce


def empty_df_from_schema(schema: Iterable[Tuple[str, str]]) -> DataFrame:
    def reducer(acc: Dict, x: Tuple[str, str]):
        acc[x[0]] = Series(dtype=x[1])
        return acc

    return DataFrame(reduce(reducer, schema, {}))


def get_datetime_cols_from_schema(schema: Iterable[Tuple[str, str]]) -> List[str]:
    def reducer(acc: List, x: Tuple[str, str]):
        if "datetime" in x[1]:
            acc.append(x[0])
        return acc

    return reduce(reducer, schema, [])
