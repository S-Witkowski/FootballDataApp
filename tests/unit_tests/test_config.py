import pytest
from Scraper.config import Config

@pytest.fixture
def config():
    return Config("config.yaml").load_config()

def test_parser_config(config):

    assert "api_consumer" in config.keys()
    assert "parser" in config.keys()
    assert "requests_limit" in config["api_consumer"].keys()
    assert "time_limit" in config["api_consumer"].keys()
    assert "sleep_time" in config["api_consumer"].keys()
    assert "tables_to_scrape" in config["parser"].keys()
