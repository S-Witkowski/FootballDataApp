import sqlite3
from pydantic import BaseModel
from typing import List, Tuple, Any, get_type_hints
from abc import ABC, abstractmethod

from Scraper.utils import type_mapping
from Scraper.models import Match, PlayerStats, ParserTech
from Scraper.constants import MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME
from Scraper.logger import logger


class Database(ABC):
    """Basic database class needed to handle interactions."""
    def __init__(self, db_name):
        self.con = self.connect(db_name)
        self.cur = self.con.cursor()

    @abstractmethod
    def connect(self, db_name: str) -> Any:
        pass

    @abstractmethod
    def create_table(self, model: BaseModel, table_name: str) -> None:
        pass

    @abstractmethod
    def delete_tables(self, tables: list) -> None:
        pass

    @abstractmethod
    def get_custom_query(self, sql_querry: str):
        pass

    @abstractmethod
    def insert_to_db(self) -> None:
        pass

class DatabaseExtended(Database):
    """Check state of db and compares it with scraped data. Expands functionality of Database class."""
    def __init__(self, db_name):
        super().__init__(db_name)
        self.db_state = self

    def check_matches_not_in_db(self, matches: List[Match]) -> List[Match]:
        """ After scraping match_ids from the website we need to compare those ids with those already in
        db. That method allows to get only matches that are NOT in db yet."""
        db_data = self.get_custom_query(f"SELECT DISTINCT match_id from matches")
        db_scraped_match_ids = [i[0] for i in db_data] if db_data else []
        return [m for m in matches if m.match_id not in db_scraped_match_ids]

    def recreate_db(self) -> None:
        """Clean and recreates db tables."""
        tables = [MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME]
        self.delete_tables(tables=tables)
        for cl, table in zip([Match, PlayerStats, ParserTech], tables):
            self.create_table(cl, table)
        logger.info(f"Tables: {tables} has been recreated.")

class SQLiteDatabase(DatabaseExtended):
    """
    Sets up the connection for SQL lite database. 
    Creates required tables, dalete them and insert data into them.
    Contains fetching functions to recognize what records are currently in the database.
    """
    def __init__(self, db_name: str):
        super().__init__(db_name)
        self.con = self.connect(db_name)
        self.cur = self.con.cursor()

    def connect(self, db_name: str) -> Any:
        return sqlite3.connect(db_name)
    
    def create_table(self, model: BaseModel, table_name: str) -> None:
        columns = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + ', '.join([f'{var} {type_mapping[t]}' for var, t in get_type_hints(model).items()])
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})')
        self.con.commit()

    def delete_tables(self, tables: list) -> None:
        for t in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS {t}")
        self.con.commit() 
        
    def get_custom_query(self, sql_querry: str) -> List[Any]:
        self.cur.execute(sql_querry)
        return self.cur.fetchall()
    
    def insert_to_db(self, table: str, columns: List[str], values: List[Tuple[Any]]) -> None:
        cols = ",".join(columns)
        sql = f"""Insert into {table} ({cols}) values ({",".join(["?" for i in columns])})"""
        self.cur.executemany(sql, values)
        self.con.commit()


