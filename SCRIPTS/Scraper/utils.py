import datetime
from typing import Union

type_mapping = {
    Union[str, None]: 'TEXT',
    Union[int, None]: 'INTEGER',
    Union[float, None]: 'REAL',
    int: 'INTEGER',
    str: 'TEXT',
    datetime.date: 'DATE',
    float: 'REAL'
}