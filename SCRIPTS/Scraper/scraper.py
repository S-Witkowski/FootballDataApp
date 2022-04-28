import requests
from requests.adapters import HTTPAdapter, Retry

from bs4 import BeautifulSoup
from pydantic.error_wrappers import ValidationError

from typing import List
import datetime
from time import sleep

from Scraper.model import Match, PlayerStats
from Scraper.pipelines import Database
from Scraper.errors import NoScoreAndFixturesInUrlException, InvalidUrlException


REQUESTS_LIMIT = 1
TIME_LIMIT = 5
TABLES_TO_SCRAPE_LIST = ['summary', 'misc']

class Scraper:
    def __init__(self):
        self.url = "https://fbref.com/"
        self.request_count = 0
        self.matches_added = 0
        self.players_stats_added = 0
        self.start_time = None

    def _call(self, url: str) -> requests.Response:
        if not self.start_time:
            self.start_time = datetime.datetime.now()

        # simple way to create limiter for api calls
        if self.request_count > REQUESTS_LIMIT:
            self._check_limiter()
        
        # sleeping for this case is the most suitable, we can do one request per three seconds
        sleep(5)

        # use retries, because website doesn't respond every time
        retry_strategy = Retry(
            total=3,
            backoff_factor=5
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        s = requests.Session()
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        resp = s.get(url, timeout=15, headers={"Content-Type":"text"})
        self.request_count += 1

        if resp.status_code == 200:
            return resp
        else:
            raise requests.exceptions.HTTPError(resp.status_code)

    def _get_soup(self, resp: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "html.parser")

    def _check_limiter(self):
        elapsed_time = (datetime.datetime.now() - self.start_time).seconds
        if elapsed_time < TIME_LIMIT:
            sleep(TIME_LIMIT - elapsed_time)
        self.request_count = 0
        self.start_time = datetime.datetime.now()

    def _compare_scraped_matches_to_db(self, last_match_id: str, matches: List[Match]) -> List[Match]:
        """ Get matches that are NOT already in the database."""
        match_num = 0
        for i, match in enumerate(matches):
            if match.match_id == last_match_id:
                match_num = i + 1
        return matches[match_num:]

    def _get_matches(self, url: str) -> List[Match]:
        """ Getting all matches for a given url."""
        resp = self._call(url)
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

        for tr in table.find_all(["tr"]): 
            round = None
            if tr.a:
                for td in tr.find_all(["td", "th"]):
                    data_stat = td.get("data-stat")
                    if data_stat == "round":
                        round = td.a.text
                    if data_stat == "date":
                        date = td.text
                    if data_stat == "squad_a":
                        home = td.a.text
                    if data_stat == "score":
                        try:
                            score = td.a.text
                        except AttributeError: # break when no score yet
                            has_score = False
                    if data_stat == "squad_b":
                        away = td.a.text
                    if td.text == "Match Report":
                        substring = td.a.get("href").replace("/en/matches/", "")
                        match_id = substring[:substring.find("/")]
                    
                if has_score:
                    m = Match(
                        round=round, 
                        date=date, 
                        home=home, 
                        score=score, 
                        away=away, 
                        match_id=match_id, 
                        season=season,
                        competition=competition)
                    match_list.append(m)
        
        return match_list

    def _get_players_stats(self, match_id: str) -> List[PlayerStats]:
        """ Get players stats for a given match id."""
        url = f"https://fbref.com/en/matches/{match_id}"
        resp = self._call(url)
        soup = self._get_soup(resp)

        tables = soup.find_all("table")
        summary_tables = []
        tables_to_scrape = []
        for t in tables:
            t_id = t.get("id")
            if t_id is not None:
                for table_name in TABLES_TO_SCRAPE_LIST:
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
                    player_stats_list.append(PlayerStats(**p))
                except:
                    print(f"Validation error: Match {match_id}, td: {tr}")

        return player_stats_list

    def scrape_missing_player_stats(self) -> None:
        """ Scrapes only the stats of players based on current state of db."""
        db = Database()
        try:
            data = db.get_not_scraped_match_ids()
            for r in data:
                match_id = r[0]
                player_stats = self._get_players_stats(match_id)
                values = [tuple(i.dict().values()) for i in player_stats]
                cols = list(PlayerStats.get_empty_dict().keys())
                db.insert_to_db("player_stats", cols, values)
                self.players_stats_added += len(values)
        finally:
            print(f"{self.players_stats_added} rows added.")
            db.con.close()

    def scrape_data(self, url: str, clear_db=False, test=False) -> None:
        """ 
        Main function of scraper. Binds whole functionality of module.

        :param url str: url to scrape data from
        :param clear_db bool: set to True to clear all tables
        :param test bool: set to True to retrive data for one match

        1. Gets matches data.
        2. Creates tables if not exist.
        3. Scrapes data.
        4. Insert data into db.
        """

        if "Scores-and-Fixtures" not in url:
            raise NoScoreAndFixturesInUrlException

        data = self._get_matches(url)

        db = Database()
        try:
            if clear_db:
                db.delete_table("matches")
                db.delete_table("player_stats")
            db.create_players_table()
            db.create_matches_table()

            last_match_id = db.get_last_match_id()
            if last_match_id != "999": # If db is not empty
                data = self._compare_scraped_matches_to_db(last_match_id, data)
            
            # getting matches data
            if data:
                if test:
                    data = data[:1]
                values = [tuple(i.dict().values()) for i in data]
                cols = list(Match.get_empty_dict().keys())
                db.insert_to_db("matches", cols, values)
                self.matches_added += len(values)

                # getting players stats data
                for match in data:
                    player_stats = self._get_players_stats(match.match_id)
                    values = [tuple(i.dict().values()) for i in player_stats]
                    cols = list(PlayerStats.get_empty_dict().keys())
                    db.insert_to_db("player_stats", cols, values)
                    self.players_stats_added += len(values)
                    
        finally:
            print(f"{self.matches_added} matches added")
            print(f"{self.players_stats_added} players stats added")
            db.con.close()
