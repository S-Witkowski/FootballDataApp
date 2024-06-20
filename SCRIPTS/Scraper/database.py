import sqlite3
import pyodbc
from pydantic import BaseModel
from typing import List, Tuple, Any, get_type_hints
from abc import ABC, abstractmethod

from Scraper.utils import type_mapping, azure_sql_type_mapping
from Scraper.models import Match, PlayerStats, ParserTech
from Scraper.constants import MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME
from Scraper.logger import logger
from Scraper.errors import NoEnvaronmentalVariableException

class DatabaseConnection(ABC):
    """" Base class for database connector. """
    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def get_cursor(self, connection: Any) -> Any:
        pass

class SQLiteDatabaseConnection(DatabaseConnection):
    """ Connector to sqlite database. """
    def __init__(self, db_name: str):
        self.db_name = db_name

    def connect(self) -> Any:
        return sqlite3.connect(self.db_name)
    
    def get_cursor(self, connection: Any) -> Any:
        return connection.cursor()
    

class AzureSQLDatabaseConnection(DatabaseConnection):
    """ Connector to azure database. """
    def __init__(self, driver: str, server_name: str, db_name: str, user_name: str, password: str):
        self._driver = driver
        self._server_name = server_name
        self._db_name = db_name
        self._user_name = user_name
        self._password = password
        if not user_name:
            raise NoEnvaronmentalVariableException("user_name")
        if not password:
            raise NoEnvaronmentalVariableException("password")

    def connect(self) -> Any:
        return pyodbc.connect(driver=self._driver, server=self._server_name, database=self._db_name, uid=self._user_name, pwd=self._password, encrypt="yes")

    def get_cursor(self, connection: Any) -> Any:
        return connection.cursor()
    
class Database(ABC):
    """Interface for database."""
    def __init__(self, database_connection: DatabaseConnection):
        self.database_connection = database_connection
        self.con = self.database_connection.connect()
        self.cur = self.database_connection.get_cursor(self.con)

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

    @abstractmethod
    def check_matches_not_in_db(self, matches: List[Match]) -> List[Match]:
        pass

    @abstractmethod
    def recreate_db(self) -> None:
        pass

class BasicDatabase(Database):
    """
    Basic SQL interface for sqlite database.
    """
    def __init__(self, database_connection: DatabaseConnection):
        super().__init__(database_connection)
    
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
        try:
            self.cur.executemany(sql, values)
            self.con.commit()
        except sqlite3.ProgrammingError as e:
            print(f"SQL command incorrect: {sql}, columns should be a list, values should be a list of tuples, got {type(values)} of {type(values[0])}")
            raise(e)

    def check_matches_not_in_db(self, matches: List[Match]) -> List[Match]:
        """ After scraping match_ids from the website we need to compare those ids with those already in
        db. That method allows to get only matches that are NOT in db yet."""
        db_data = self.get_custom_query(f"SELECT DISTINCT match_id from matches")
        db_scraped_match_ids = [i[0] for i in db_data] if db_data else []
        matches = [m for m in matches if m.match_id not in db_scraped_match_ids]
        return matches if matches else []

    def recreate_db(self) -> None:
        """Clean and recreates db tables."""
        tables = [MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME, PARSER_TECH_TABLE_NAME]
        self.delete_tables(tables=tables)
        for cl, table in zip([Match, PlayerStats, ParserTech], tables):
            self.create_table(cl, table)
        logger.info(f"Tables: {tables} has been recreated.")


class AzureDatabase(BasicDatabase):
    """
    Database interface for Azure SQL database.
    """
    def __init__(self, database_connection: DatabaseConnection):
        super().__init__(database_connection)
    
    def create_table(self, model: BaseModel, table_name: str) -> None:
        columns = "id INT identity(1,1), " + ', '.join([f'{var} {azure_sql_type_mapping[t]}' for var, t in get_type_hints(model).items()])
        self.cur.execute(f'CREATE TABLE {table_name} ({columns})')
        self.con.commit()