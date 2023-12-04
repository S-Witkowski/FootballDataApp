import pytest
from Scraper.database import SQLiteDatabase
from Scraper.models import Match, PlayerStats
from Scraper.constants import MATCHES_TABLE_NAME, PLAYER_STATS_TABLE_NAME

@pytest.fixture
def sqlite_db():
    return SQLiteDatabase(":memory:")

def test_create_matches_table(sqlite_db):
    sqlite_db.create_table(Match, MATCHES_TABLE_NAME)
    # Check if the table exists
    sqlite_db.cur.execute("SELECT c.name FROM pragma_table_info('matches') c")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert columns
    for attribute in Match.get_empty_dict().keys():
        assert attribute in columns
        
def test_create_players_table(sqlite_db):
    sqlite_db.create_table(PlayerStats, PLAYER_STATS_TABLE_NAME)
    # Check if the table exists
    sqlite_db.cur.execute("SELECT c.name FROM pragma_table_info('player_stats') c")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert columns
    for attribute in PlayerStats.get_empty_dict().keys():
        assert attribute in columns

def test_delete_tables(sqlite_db):
    sqlite_db.create_table(Match, MATCHES_TABLE_NAME)
    sqlite_db.create_table(PlayerStats, PLAYER_STATS_TABLE_NAME)
    sqlite_db.delete_tables(["matches", "player_stats"])
    # Check if tables are empty
    sqlite_db.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert "matches" not in columns
    assert "player_stats" not in columns

def test_insert_to_db(sqlite_db):
    sqlite_db.create_table(Match, MATCHES_TABLE_NAME)
    sqlite_db.insert_to_db("matches", ["round"], [("Round 1",)])
    # Check if data is inserted
    sqlite_db.cur.execute("SELECT * FROM matches")
    data = sqlite_db.cur.fetchall()
    assert data == [(1, "Round 1", None, None, None, None, None, None, None)]