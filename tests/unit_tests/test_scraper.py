import pytest
from unittest.mock import Mock, MagicMock, patch
from Scraper.scraper import Scraper
from Scraper.models import PlayerStats, Match
from Scraper.errors import NoScoreAndFixturesInUrlException
from Scraper.config import Config
from Scraper.database import SQLiteDatabase
from Scraper.constants import MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME

import datetime 

@pytest.fixture
def config():
    return Config('config.yaml').load_config()

@pytest.fixture
def mock_parser():
    return MagicMock()

@pytest.fixture
def mock_database():
    return MagicMock()

@pytest.fixture
def mock_db_state():
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
        competition="Example League"),
    Match(
        date=datetime.date(2023, 12, 18),
        home="TeamA",
        score="2-0",
        away="TeamD",
        match_id="125",
        season="2023-2024",
        competition="Example League")
    ]

@pytest.fixture
def players_mock_data():
    return [
    PlayerStats(match_id="123", team="TeamA", player="player_a", player_id="1"),
    PlayerStats(match_id="124", team="TeamB", player="player_b", player_id="2"),
    PlayerStats(match_id="125", team="TeamD", player="player_c", player_id="3"),
    PlayerStats(match_id="125", team="TeamA", player="player_a", player_id="1")
    ]

def test_scrape_data(mock_parser: MagicMock, mock_database: MagicMock, config: MagicMock, matches_mock_data: list, players_mock_data: list):
    scraper = Scraper(mock_parser, mock_database)
    mock_database.db_state.check_matches_not_in_db.return_value = matches_mock_data
    mock_parser.get_matches.return_value = matches_mock_data
    mock_parser.get_players_stats = MagicMock(side_effect=lambda m, **kwargs: [p for p in players_mock_data if p.match_id == m])
    scraper.scrape_data(config["integration_tests"]["data_test_url"])

    assert scraper.matches_added == len(matches_mock_data)
    # handle player_stats correct number of times it was added to db for each match
    m_dict = {m.match_id: [] for m in matches_mock_data}
    for p in players_mock_data:
        m_dict[p.match_id].append(p.player_id)
    assert scraper.players_stats_added == len(sum(m_dict.values(), []))

def test_scrape_data_with_number_of_matches_to_scrape(mock_database: MagicMock, mock_parser: MagicMock, config: MagicMock, matches_mock_data: list, players_mock_data: list):
    scraper = Scraper(mock_parser, mock_database)
    mock_database.db_state.check_matches_not_in_db.return_value = matches_mock_data
    mock_parser.get_matches.return_value = matches_mock_data
    mock_parser.get_players_stats.return_value = players_mock_data
    scraper.scrape_data(config["integration_tests"]["data_test_url"], number_of_matches_to_scrape=1)
    assert scraper.matches_added == 1

def test_scrape_data_with_invalid_url(mock_database: MagicMock, mock_parser: MagicMock):
    scraper = Scraper(mock_parser, mock_database)
    with pytest.raises(NoScoreAndFixturesInUrlException) as exc_info:
        scraper.scrape_data("https://example.com")
    
def test_scrape_data_with_recreate_db(mock_database: MagicMock, mock_parser: MagicMock, config):
    sqlite_db = SQLiteDatabase(":memory:")
    sqlite_db.db_state.recreate_db()
    scraper = Scraper(mock_parser, sqlite_db)
    scraper.scrape_data = MagicMock()
    # Check if tables are NOT empty
    sqlite_db.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert MATCHES_TABLE_NAME in columns
    assert PLAYER_STATS_TABLE_NAME in columns
    assert PARSER_TECH_TABLE_NAME in columns