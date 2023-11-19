import requests
from requests.adapters import HTTPAdapter, Retry

import datetime
from time import sleep

#from Scraper.logger import logger

class APIConsumer:
    """Interact with website, handling HTTP responses."""
    def __init__(self, config: dict):
        self.config = config
        self.request_count_per_batch = 0
        self.start_time = None
        self.api_calls = 0

    def call(self, url: str) -> requests.Response:
        if not self.start_time:
            self.start_time = datetime.datetime.now()

        # simple way to create limiter for API calls
        if self.request_count_per_batch > self.config["api_consumer"]["requests_limit"]:
            self._check_limiter()

        # sleeping for this case is the most suitable, we can do one request per three seconds
        sleep(self.config["api_consumer"]["sleep_time"])

        # use retries, because the website doesn't respond every time
        retry_strategy = Retry(
            total=3,
            backoff_factor=5
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        s = requests.Session()
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        resp = s.get(url, timeout=15, headers={"Content-Type": "text"})
        self.api_calls += 1
        self.request_count_per_batch += 1

        if resp.status_code == 200:
            return resp
        else:
            #logger.error(f"Couldn't get 200 status code, received: {resp.status_code}")
            raise requests.exceptions.HTTPError(resp.status_code)

    def _check_limiter(self):
        elapsed_time = (datetime.datetime.now() - self.start_time).seconds
        if elapsed_time < self.config["api_consumer"]["time_limit"]:
            sleep(self.config["api_consumer"]["time_limit"] - elapsed_time)
        self.request_count_per_batch = 0
        self.start_time = datetime.datetime.now()