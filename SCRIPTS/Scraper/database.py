import sqlite3
from typing import List, Tuple, Any, get_type_hints
from abc import ABC, abstractmethod
from Scraper.models import Match, PlayerStats
from Scraper.utils import type_mapping

class Database(ABC):
    def __init__(self, db_name):
        self.con = self.connect(db_name)
        self.cur = self.con.cursor()

    @abstractmethod
    def connect(self, db_name) -> Any:
        pass

    @abstractmethod
    def create_matches_table(self):
        pass
    
    @abstractmethod
    def create_players_table(self):
        pass   

    @abstractmethod
    def delete_tables(self):
        pass

    @abstractmethod
    def get_not_scraped_match_ids(self):
        pass

    @abstractmethod
    def get_last_match_id(self):
        pass

    @abstractmethod
    def insert_to_db(self):
        pass

class SQLiteDatabase(Database):
    """
    Sets up the connection for SQL lite database. 
    Creates required tables, dalete them and insert data into them.
    Contains fetching functions to recognize what records are currently in the database.
    """
    def __init__(self, db_name: str):
        self.con = self.connect(db_name)
        self.cur = self.con.cursor()

    def connect(self, db_name: str) -> Any:
        return sqlite3.connect(db_name)
    
    def create_matches_table(self):
        columns = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + ', '.join([f'{var} {type_mapping[t]}' for var, t in get_type_hints(Match).items()])
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS matches ({columns})')
        self.con.commit()

    def create_players_table(self):
        columns = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + ', '.join([f'{var} {type_mapping[t]}' for var, t in get_type_hints(PlayerStats).items()])
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS player_stats ({columns})')        
        self.con.commit()     
    
    def delete_tables(self, tables: list) -> None:
        for t in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS {t}")
        self.con.commit() 

    def get_not_scraped_match_ids(self):
        """ Gets match ids from db if there is a missing data in players table."""
        self.cur.execute("select match_id from matches where match_id not in (\
            SELECT match_id FROM player_stats)")
        return self.cur.fetchall()

    def get_last_match_id(self) -> str:
        """ Gets match id that was last scraped record. """
        self.cur.execute("select match_id from matches where id = (Select max(id) from matches)")
        row = self.cur.fetchone()
        if row:
            return row[0]
        else:
            return "999"
    
    def insert_to_db(self, table: str, columns: List[str], values: List[Tuple[Any]]) -> None:
        cols = ",".join(columns)
        sql = f"""Insert into {table} ({cols}) values ({",".join(["?" for i in columns])})"""
        self.cur.executemany(sql, values)
        self.con.commit()



