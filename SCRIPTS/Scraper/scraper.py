from typing import List, Union
from tqdm import tqdm

from Scraper.models import Match, PlayerStats, ParserTech
from Scraper.errors import NoScoreAndFixturesInUrlException
from Scraper.logger import logger
from Scraper.database import DatabaseExtended
from Scraper.parser import Parser
from Scraper.constants import MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME


        
class Scraper:
    """Interacts with database."""
    def __init__(self, parser: Parser, db: DatabaseExtended):
        self.parser = parser
        self.db = db
        self.url = "https://fbref.com/"
        self.matches_added = 0
        self.players_stats_added = 0
    
    def _process_player_stats(self, match_id: str) -> None:
        """Scrapes and inserts player stats for a given match_id."""
        player_stats = self.parser.get_players_stats(match_id, db=self.db)
        values = [tuple(i.model_dump().values()) for i in player_stats]
        cols = list(PlayerStats.get_empty_dict().keys())
        self.db.insert_to_db(PLAYER_STATS_TABLE_NAME, cols, values)
        self.players_stats_added += len(values)

    def _process_matches(self, data: List[Match], number_of_matches_to_scrape: Union[int, None]) -> None:
        """Processes and inserts matches data."""
        if number_of_matches_to_scrape is not None:
            data = data[:number_of_matches_to_scrape]
        # Getting players stats data
        for match in tqdm(data):
            self._process_player_stats(match.match_id)
        values = [tuple(i.model_dump().values()) for i in data]
        cols = list(Match.get_empty_dict().keys())
        self.db.insert_to_db(MATCHES_TABLE_NAME, cols, values)
        self.matches_added += len(values)

    def scrape_data(self, url: str, number_of_matches_to_scrape: Union[int, None]=None) -> None:
        """ 
        Main function of scraper. Binds whole functionality of module.

        :param url str: url to scrape data from
        :param number_of_matches_to_scrape int | None: set the number of matches to retrive

        1. Gets matches data.
        2. Compares it to current db_state.
        3. Processes the data.
        4. Insert data into db.
        """

        if "Scores-and-Fixtures" not in url:
            raise NoScoreAndFixturesInUrlException

        try:
            match_data_from_url = self.parser.get_matches(url, db=self.db)
            match_data = self.db.db_state.check_matches_not_in_db(match_data_from_url)
            logger.info(f"There will be {number_of_matches_to_scrape if number_of_matches_to_scrape and len(match_data) < number_of_matches_to_scrape else len(match_data)} matches to process on {url}")
            if match_data:
                self._process_matches(match_data, number_of_matches_to_scrape)
        except Exception as e:
            logger.exception(f"Expection occured in scraper.scrape_data", exc_info=True)
        finally:
            logger.info(f"{self.matches_added}/{self.parser.match_processed} matches added")
            logger.info(f"{self.players_stats_added}/{self.parser.player_stats_processed} players stats added")
            logger.info(f"Total api calls: {self.parser.api_consumer.api_calls}")
