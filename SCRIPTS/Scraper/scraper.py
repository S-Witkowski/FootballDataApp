from typing import List, Union

from Scraper.models import Match, PlayerStats
from Scraper.errors import NoScoreAndFixturesInUrlException
from Scraper.logger import logger
from Scraper.database import Database
from Scraper.parser import Parser

    
class Scraper:
    """Interacts with database."""
    def __init__(self, parser: Parser, db: Database):
        self.parser = parser
        self.db = db
        self.url = "https://fbref.com/"
        self.matches_added = 0
        self.players_stats_added = 0

    @staticmethod
    def _compare_scraped_matches_to_db(last_match_id: str, matches: List[Match]) -> List[Match]:
        """ Get matches that are NOT already in the database."""
        match_num = 0
        for i, match in enumerate(matches):
            if match.match_id == last_match_id:
                match_num = i + 1
        return matches[match_num:]
    
    def _process_player_stats(self, match_id: str) -> None:
        """Scrapes and inserts player stats for a given match_id."""
        player_stats = self.parser.get_players_stats(match_id)
        values = [tuple(i.model_dump().values()) for i in player_stats]
        cols = list(PlayerStats.get_empty_dict().keys())
        self.db.insert_to_db("player_stats", cols, values)
        self.players_stats_added += len(values)

    def _process_matches(self, data: List[Match], number_of_matches_to_scrape: Union[int, None]) -> None:
        """Processes and inserts matches data."""
        if number_of_matches_to_scrape is not None:
            data = data[:number_of_matches_to_scrape]
        values = [tuple(i.model_dump().values()) for i in data]
        cols = list(Match.get_empty_dict().keys())
        self.db.insert_to_db("matches", cols, values)
        self.matches_added += len(values)

        # Getting players stats data
        for match in data:
            self._process_player_stats(match.match_id)

    def scrape_missing_player_stats(self) -> None:
        """ Scrapes only the stats of players based on current state of db."""
        try:
            data = self.db.get_not_scraped_match_ids()
            for r in data:
                self._process_player_stats(r[0])
        except Exception as e:
            logger.exception("Error getting missing players stats with data: {data}", exc_info=True)
        finally:
            logger.info(f"{self.players_stats_added} rows added.")
            self.db.con.close()

    def scrape_data(self, url: str, clear_db: bool=False, number_of_matches_to_scrape: Union[int, None]=None) -> None:
        """ 
        Main function of scraper. Binds whole functionality of module.

        :param url str: url to scrape data from
        :param clear_db bool: set to True to clear all tables
        :param number_of_matches_to_scrape int | None: set the number of matches to retrive

        1. Gets matches data.
        2. Creates tables if not exist.
        3. Scrapes data.
        4. Insert data into db.
        """

        if "Scores-and-Fixtures" not in url:
            raise NoScoreAndFixturesInUrlException

        data = self.parser.get_matches(url)

        try:
            if clear_db:
                tables = ["matches", "player_stats"]
                self.db.delete_tables(tables=tables)
                logger.info(f"Tables: {tables} has been recreated.")
            self.db.create_players_table()
            self.db.create_matches_table()

            last_match_id = self.db.get_last_match_id()
            if last_match_id != "999": # If db is not empty
                data = self._compare_scraped_matches_to_db(last_match_id, data)
            
            if data:
                self._process_matches(data, number_of_matches_to_scrape)
                    
        finally:
            logger.info(f"{self.matches_added}/{self.parser.match_processed} matches added")
            logger.info(f"{self.players_stats_added}/{self.parser.player_stats_processed} players stats added")
            logger.info(f"Total api calls: {self.parser.api_consumer.api_calls}")
            if self.db:
                self.db.con.close()
