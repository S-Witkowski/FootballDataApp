import pytest
from unittest.mock import MagicMock
from Scraper.database import BasicDatabase, SQLiteDatabaseConnection
from Scraper.models import Match
import datetime 

@pytest.fixture
def sqlite_db():
    db_conn = SQLiteDatabaseConnection(":memory:")
    return BasicDatabase(db_conn)

@pytest.fixture
def mock_database():
    return MagicMock()

@pytest.fixture
def matches_mock_data():
    return [
    Match(
        date=datetime.date(2023, 11, 18),
        home="TeamA",
        score="3-1",
        away="TeamB",
        match_id="123",
        season="2023-2024",
        competition="Example League"),
    Match(
        date=datetime.date(2023, 12, 18),
        home="TeamC",
        score="1-0",
        away="TeamD",
        match_id="124",
        season="2023-2024",
        competition="Example League")
    ]

def test_check_matches_not_in_db(sqlite_db: MagicMock, matches_mock_data: list):
    sqlite_db.get_custom_query = MagicMock(return_value=[("123",)])
    result = sqlite_db.check_matches_not_in_db(matches_mock_data)
    assert result == [m for m in matches_mock_data if m.match_id != "123"]

def test_check_matches_not_in_db_empty_db(sqlite_db: MagicMock, matches_mock_data: list):
    sqlite_db.get_custom_query = MagicMock(return_value=[])
    result = sqlite_db.check_matches_not_in_db(matches_mock_data)
    assert result == matches_mock_data

