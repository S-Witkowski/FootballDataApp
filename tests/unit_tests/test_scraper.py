import pytest
from unittest.mock import Mock, MagicMock, patch
from Scraper.scraper import Scraper
from Scraper.models import PlayerStats, Match
from Scraper.errors import NoScoreAndFixturesInUrlException
from Scraper.config import Config

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

def test_compare_scraped_matches_to_db():
    last_match_id = "123"
    matches = [Mock(match_id="123"), Mock(match_id="456"), Mock(match_id="789")]
    result = Scraper._compare_scraped_matches_to_db(last_match_id, matches)
    assert result == [matches[1], matches[2]]

def test_scrape_missing_player_stats(mock_database, mock_parser):
    scraper = Scraper(mock_parser, mock_database)
    mock_database.get_not_scraped_match_ids.return_value = [("123",)]
    mock_parser.get_players_stats.return_value = [PlayerStats(match_id="123", team="TeamA", player="player", player_id="12345")]
    scraper.scrape_missing_player_stats()

    assert scraper.matches_added == 0
    assert scraper.players_stats_added == 1

def test_scrape_data_with_clear_db(mock_database, mock_parser):
    scraper = Scraper(mock_parser, mock_database)
    mock_parser.get_matches.return_value = [Match(
        date=datetime.date(2023, 11, 18),
        home="TeamA",
        score="3-1",
        away="TeamB",
        match_id="123",
        season="2023-2024",
        competition="Example League")
    ]
    mock_database.get_last_match_id.return_value = "999"
    mock_parser.get_players_stats.return_value = [PlayerStats(match_id="123", team="TeamA", player="player", player_id="12345")]

    scraper.scrape_data("https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures", clear_db=True)

    assert scraper.matches_added == 1
    assert scraper.players_stats_added == 1

def test_scrape_data_without_clear_db(mock_database, mock_parser):
    scraper = Scraper(mock_parser, mock_database)
    mock_parser.get_matches.return_value = [Match(
        date=datetime.date(2023, 11, 18),
        home="TeamA",
        score="3-1",
        away="TeamB",
        match_id="123",
        season="2023-2024",
        competition="Example League")
    ]
    mock_database.get_last_match_id.return_value = "123"
    mock_parser.get_players_stats.return_value = [PlayerStats(match_id="123", team="TeamA", player="player", player_id="12345")]

    scraper.scrape_data("https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures", clear_db=False)

    assert scraper.matches_added == 0
    assert scraper.players_stats_added == 0

def test_scrape_data_with_number_of_matches_to_scrape(mock_database, mock_parser, config):
    scraper = Scraper(mock_parser, mock_database)
    mock_data = [
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
        competition="Example League")]
    mock_parser.get_matches.return_value = mock_data
    mock_database.get_last_match_id.return_value = "999"

    with patch('SCRIPTS.Scraper.database.Database', autospec=True):
        scraper.scrape_data(config["integration_tests"]["data_test_url"], clear_db=False, number_of_matches_to_scrape=1)

    assert scraper.matches_added == 1

def test_scrape_data_with_invalid_url(mock_database, mock_parser):
    scraper = Scraper(mock_parser, mock_database)
    print(NoScoreAndFixturesInUrlException)
    with pytest.raises(NoScoreAndFixturesInUrlException) as exc_info:
        scraper.scrape_data("https://example.com")

    print(f"Exception message: {exc_info.value}")
    assert str(exc_info.value) == "There is no 'Scores-and-Fixtures' in the URL."
    
