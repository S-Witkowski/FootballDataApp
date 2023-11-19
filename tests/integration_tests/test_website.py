import pytest
import requests
from unittest.mock import MagicMock, patch
from SCRIPTS.Scraper.api_consumer import APIConsumer
from SCRIPTS.Scraper.config import Config
from SCRIPTS.Scraper.parser import Parser
from SCRIPTS.Scraper.logger import logger


@pytest.fixture
def config():
    return Config('config.yaml').load_config()

def test_website_is_up(config):
    api_consumer = APIConsumer(config)
    resp = api_consumer.call(config["integration_tests"]["base_url"])
    assert resp.status_code == 200

def test_player_stats_data_table_in_line_with_model(config):
    api_consumer = APIConsumer(config)
    parser = Parser(api_consumer, config)
    match_id = config["integration_tests"]["test_match_id"]
    player_stats_lst = parser.get_players_stats(match_id)
    missing_stats = [(var, val) for var, val in player_stats_lst[0] if val is None]
    try:
        assert missing_stats == []
    except AssertionError as e:
        logger.error(f"No such player_stats on the webiste: {missing_stats}. Check naming on the website.", exc_info=True)    
        raise e