from requests import Response

from bs4 import BeautifulSoup
from pydantic import ValidationError

from typing import List

from Scraper.models import Match, PlayerStats
from Scraper.errors import InvalidUrlException
from Scraper.logger import logger
from Scraper.api_consumer import APIConsumer

class Parser:
    """Parsing HTTP response into python data types."""
    def __init__(self, api_consumer: APIConsumer, config: dict):
        self.api_consumer = api_consumer
        self.config = config
        self.player_stats_processed = 0
        self.match_processed = 0

    def _get_soup(self, resp: Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "html.parser")
    
    def get_matches(self, url: str) -> List[Match]:
        """ Getting all matches for a given url."""
        resp = self.api_consumer.call(url)
        soup = self._get_soup(resp)
        try:
            table = soup.find(id="all_sched").tbody
        except AttributeError:
            raise InvalidUrlException(url)
        ss = soup.find(id="meta").h1.text.strip()
        season = ss[:ss.find(" ")]
        competition = ss.replace(" Scores & Fixtures", "")[len(season)+1:]

        match_list = []

        # break flag when match hasn't been played yet
        has_score = True 
        # parameters to fill with values
        match_dict = Match.get_empty_dict()
        for tr in table.find_all(["tr"]): 
            if tr.a:
                for td in tr.find_all(["td", "th"]):
                    data_stat = td.get("data-stat")
                    if data_stat == "round":
                        match_dict["round"] = td.a.text
                    elif data_stat == "date":
                        match_dict["date"] = td.text
                    elif data_stat == "home_team":
                        match_dict["home"] = td.a.text
                    elif data_stat == "score":
                        try:
                            match_dict["score"] = td.a.text
                        except AttributeError: # break when no score yet
                            has_score = False
                    elif data_stat == "away_team":
                        match_dict["away"] = td.a.text
                    elif td.text == "Match Report":
                        substring = td.a.get("href").replace("/en/matches/", "")
                        match_dict["match_id"] = substring[:substring.find("/")]
                    
                if has_score:
                    try:
                        match_dict["season"] = season
                        match_dict["competition"] = competition
                        if match_dict['match_id'] not in [i.match_id for i in match_list]:
                            self.match_processed += 1
                            match_list.append(Match(**match_dict))
                    except ValidationError as e:
                        logger.error(f"Match cannot be created with those params: {match_dict}", exc_info=True)

        return match_list

    def get_players_stats(self, match_id: str) -> List[PlayerStats]:
        """ Get players stats for a given match id."""
        url = f"https://fbref.com/en/matches/{match_id}"
        resp = self.api_consumer.call(url)
        soup = self._get_soup(resp)

        tables = soup.find_all("table")
        summary_tables = []
        tables_to_scrape = []
        player_id_list = []
        for t in tables:
            t_id = t.get("id")
            if t_id is not None:
                for table_name in self.config["parser"]["tables_to_scrape"]:
                    if table_name in t_id:
                        tables_to_scrape.append(t)
                    if t_id is not None and 'summary' in t_id:
                        summary_tables.append(t)

        player_stats_list = []

        for table in summary_tables: # teams
            for tr in table.tbody.find_all("tr"): # players
                p = PlayerStats.get_empty_dict()
                p["match_id"] = match_id
                p["team"] = table.caption.text.replace(" Player Stats Table", "")
                p["player_id"] = tr.th.get("data-append-csv")
                for tts in tables_to_scrape: # tables
                    for tr in tts.tbody.find_all("tr"): # rows
                        if tr.th.get("data-append-csv") == p["player_id"]:
                            for td in tr.find_all(["td", "th"]): # cols
                                data_stat = td.get("data-stat")
                                for k in p.keys():
                                    if k == data_stat:
                                        p[k] = td.text.strip()
                try:
                    if p['player_id'] not in player_id_list:
                        self.player_stats_processed += 1
                        player_id_list.append(p['player_id'])
                        player_stats_list.append(PlayerStats(**p))
                except Exception as e:
                    logger.error(f"Validation error: Match {match_id}, player: {p['player_id']}, data: {tr}", exc_info=True)
                
        return player_stats_list