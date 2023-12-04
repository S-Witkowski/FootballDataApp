import pytest
import datetime

from Scraper.models import Match, PlayerStats, ParserTech
from Scraper.constants import MATCH_PARSE_TYPE, PARSER_TECH_TABLE_NAME, PLAYER_PARSE_TYPE

def test_parser_config():
    assert ParserTech(
        match_id='123',
        player_id=None,
        parse_date=datetime.datetime.now(),
        parse_type=MATCH_PARSE_TYPE,
        error_msg=None
    )