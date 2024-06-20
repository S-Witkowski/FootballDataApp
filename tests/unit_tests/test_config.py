import pytest
import os
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

# not needed if sqlite is used
# def test_env_variables(config):
#     assert "azure_uid" in config["azure_connection"].keys()
#     assert "azure_pwd" in config["azure_connection"].keys()
#     assert os.getenv(config["azure_connection"]["azure_uid"])
#     assert os.getenv(config["azure_connection"]["azure_pwd"])