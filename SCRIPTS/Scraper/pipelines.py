import sqlite3
from typing import List, Tuple, Any

class Database:
    """
    Sets up the connection for database. 
    Creates required tables, dalete them and insert data into them.
    Contains fetching functions to recognize what records are currently in the database.
    """
    def __init__(self):
        self.con = sqlite3.connect("football_db_prod.db")
        self.cur = self.con.cursor()
    
    def create_matches_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round text, 
                date date, 
                home text,
                score text,
                away text,
                match_id text,
                season text,
                competition text)
               """)
        self.con.commit()

    def create_players_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id text,
            team text,
            player text,
            player_id text,
            minutes INTEGER,
            goals INTEGER,
            assists INTEGER,
            shots_total INTEGER,
            cards_yellow INTEGER,
            cards_red INTEGER,
            touches INTEGER,
            pressures INTEGER,
            tackles INTEGER,
            interceptions INTEGER,
            blocks INTEGER,
            xg real,
            xa real,
            sca INTEGER,
            gca INTEGER,
            passes_completed INTEGER,
            passes INTEGER,
            progressive_passes INTEGER,
            dribbles_completed INTEGER,
            dribbles INTEGER,
            fouls INTEGER,
            fouled INTEGER
            )
               """)
        self.con.commit()     
    
    def delete_table(self, table: str) -> None:
        self.cur.execute(f"DELETE FROM {table}")
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



