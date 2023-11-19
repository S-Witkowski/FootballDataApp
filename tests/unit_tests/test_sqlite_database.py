import pytest
from Scraper.database import SQLiteDatabase
from Scraper.models import Match, PlayerStats

@pytest.fixture
def sqlite_db():
    return SQLiteDatabase(":memory:")

def test_create_matches_table(sqlite_db):
    sqlite_db.create_matches_table()

    # Check if the table exists
    sqlite_db.cur.execute("SELECT c.name FROM pragma_table_info('matches') c")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert columns
    for attribute in Match.get_empty_dict().keys():
        assert attribute in columns
        
def test_create_players_table(sqlite_db):
    sqlite_db.create_players_table()

    # Check if the table exists
    sqlite_db.cur.execute("SELECT c.name FROM pragma_table_info('player_stats') c")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert columns
    for attribute in PlayerStats.get_empty_dict().keys():
        assert attribute in columns

def test_delete_tables(sqlite_db):
    # Create tables
    sqlite_db.create_matches_table()
    sqlite_db.create_players_table()

    # Delete tables
    sqlite_db.delete_tables(["matches", "player_stats"])

    # Check if tables are empty
    sqlite_db.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    columns = [x[0] for x in sqlite_db.cur.fetchall()]
    assert "matches" not in columns
    assert "player_stats" not in columns

def test_get_not_scraped_match_ids_false(sqlite_db):
    # Create tables
    sqlite_db.create_matches_table()
    sqlite_db.create_players_table()

    # Insert dummy data
    sqlite_db.insert_to_db("matches", ["match_id"], [("123",)])
    sqlite_db.insert_to_db("player_stats", ["match_id"], [("123",)])

    # Check for not scraped match IDs
    not_scraped_ids = sqlite_db.get_not_scraped_match_ids()
    assert not not_scraped_ids

def test_get_not_scraped_match_ids_true(sqlite_db):
    # Create tables
    sqlite_db.create_matches_table()
    sqlite_db.create_players_table()

    # Insert dummy data
    sqlite_db.insert_to_db("matches", ["match_id"], [("123",)])

    # Check for not scraped match IDs
    not_scraped_ids = sqlite_db.get_not_scraped_match_ids()
    assert not_scraped_ids == [("123",)]
    
def test_get_last_match_id(sqlite_db):
    # Create table
    sqlite_db.create_matches_table()

    # Insert dummy data
    sqlite_db.insert_to_db("matches", ["match_id"], [("123",), ("456",)])

    # Check the last match ID
    last_match_id = sqlite_db.get_last_match_id()
    assert last_match_id == "456"

def test_insert_to_db(sqlite_db):
    # Create table
    sqlite_db.create_matches_table()

    # Insert data
    sqlite_db.insert_to_db("matches", ["round"], [("Round 1",)])

    # Check if data is inserted
    sqlite_db.cur.execute("SELECT * FROM matches")
    data = sqlite_db.cur.fetchall()
    assert data == [(1, "Round 1", None, None, None, None, None, None, None)]