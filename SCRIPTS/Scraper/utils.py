import datetime
from typing import Union

type_mapping = {
    Union[str, None]: 'TEXT',
    Union[int, None]: 'INTEGER',
    Union[float, None]: 'REAL',
    int: 'INTEGER',
    str: 'TEXT',
    datetime.date: 'DATE',
    datetime.datetime: 'DATETIME',
    float: 'REAL'
}

azure_sql_type_mapping = {
    Union[str, None]: 'VARCHAR(100)',
    Union[int, None]: 'INT',
    Union[float, None]: 'REAL',
    int: 'INT',
    str: 'VARCHAR(100)',
    datetime.date: 'DATE',
    datetime.datetime: 'DATETIME',
    float: 'REAL'
}