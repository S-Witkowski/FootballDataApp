from requests import Response

from bs4 import BeautifulSoup
from pydantic import ValidationError

from typing import List, Optional

from Scraper.models import Match, PlayerStats, ParserTech
from Scraper.errors import InvalidUrlException
from Scraper.logger import logger
from Scraper.api_consumer import APIConsumer
from Scraper.database import Database
from Scraper.constants import MATCH_PARSE_TYPE, PARSER_TECH_TABLE_NAME, PLAYER_PARSE_TYPE

class Parser:
    """Parsing HTTP response into python data types."""
    def __init__(self, api_consumer: APIConsumer, config: dict):
        self.api_consumer = api_consumer
        self.config = config
        self.player_stats_processed = 0
        self.match_processed = 0

    def _get_soup(self, resp: Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "html.parser")
    
    def get_matches(self, url: str, db: Optional[Database]=None) -> List[Match]:
        """ Getting all matches for a given url. Inserting tech info into db if needed. """
        resp = self.api_consumer.call(url)
        soup = self._get_soup(resp)
        try:
            table = soup.find(id="all_sched").tbody
        except AttributeError:
            raise InvalidUrlException(url)
        ss = soup.find(id="meta").h1.text.strip()
        season = ss[:ss.find(" ")]
        competition = ss.replace(" Scores & Fixtures", "")[len(season)+1:]

        match_id_list = []
        match_list = []
        parser_tech_data_list = []
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
                if has_score and match_dict['match_id'] not in match_id_list:
                    try:
                        match_id_list.append(match_dict['match_id'])
                        self.match_processed += 1
                        match_dict["season"] = season
                        match_dict["competition"] = competition
                        match_list.append(Match(**match_dict))
                        error_msg = None
                    except ValidationError as e:
                        error_msg = f"Match cannot be created with those params: {match_dict}"
                        logger.error(error_msg, exc_info=True)
                    parser_tech_data_list.append(ParserTech(
                        match_id=match_dict['match_id'],
                        player_id=None,
                        parse_date=self.api_consumer.last_api_call_data,
                        parse_type=MATCH_PARSE_TYPE,
                        error_msg=error_msg
                        ))
        if db:
            values = [tuple(i.model_dump().values()) for i in parser_tech_data_list]
            cols = list(ParserTech.get_empty_dict().keys())
            db.insert_to_db(PARSER_TECH_TABLE_NAME, cols, values)
        return match_list

    def get_players_stats(self, match_id: str, db: Optional[Database]=None) -> List[PlayerStats]:
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
        parser_tech_data_list = []
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
                                        if td.text.strip() == '':
                                            p[k] = None
                                        else:
                                            p[k] = td.text.strip()
                if p['player_id'] not in player_id_list:
                    try:
                        self.player_stats_processed += 1
                        player_id_list.append(p['player_id'])
                        player_stats_list.append(PlayerStats(**p))
                        error_msg = None
                    except Exception as e:
                        error_msg = f"Validation error: Match {match_id}, player: {p['player_id']}, data: {tr}"
                        logger.error(error_msg, exc_info=True)
                    parser_tech_data_list.append(ParserTech(
                        match_id=match_id,
                        player_id=p['player_id'],
                        parse_date=self.api_consumer.last_api_call_data,
                        parse_type=PLAYER_PARSE_TYPE,
                        error_msg=error_msg
                        ))
        if db:
            values = [tuple(i.model_dump().values()) for i in parser_tech_data_list]
            cols = list(ParserTech.get_empty_dict().keys())
            db.insert_to_db(PARSER_TECH_TABLE_NAME, cols, values)
        return player_stats_list