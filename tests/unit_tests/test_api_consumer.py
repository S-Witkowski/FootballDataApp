import pytest
import requests
from unittest.mock import MagicMock, patch
from Scraper.api_consumer import APIConsumer

@pytest.fixture
def api_consumer_config():
    return {
        "api_consumer": {
            "requests_limit": 1,
            "sleep_time": 5,
            "time_limit": 5
        }
    }
@patch("requests.Session.get")
def test_call_successful_request(mock_get, api_consumer_config):
    api_consumer = APIConsumer(api_consumer_config)
    url = "https://fbref.com/"
    mock_response = MagicMock(status_code=200)
    mock_get.return_value = mock_response
    resp = api_consumer.call(url)
    assert resp.status_code == 200

@patch("requests.Session.get")
def test_call_unsuccessful_request(mock_get, api_consumer_config):
    api_consumer = APIConsumer(api_consumer_config)
    url = "https://fbref.com/"
    
    # Mock the requests.Session.get method to simulate a 404 response
    mock_response = MagicMock(status_code=404)
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api_consumer.call(url)
        assert excinfo == requests.exceptions.HTTPError
