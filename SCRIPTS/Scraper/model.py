import pydantic
import datetime

from typing import Optional

""" 
Pydantic data model. 
Names of columns should be the same as the names in sql database and the names of the data-stats on website.
"""

class Match(pydantic.BaseModel):
    round: Optional[str] or None = None # there is no round for ligue matches
    date: datetime.date
    home: str
    score: str
    away: str
    match_id: str
    season: str
    competition: str
    @classmethod
    def get_empty_dict(cls,alias=False):
        fields_list = list(cls.schema(alias).get("properties").keys())
        return dict(zip(fields_list, [None for i in fields_list]))

class PlayerStats(pydantic.BaseModel):
    match_id: str
    team: str
    player: str
    player_id: str
    minutes: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    shots_total: Optional[int] = None
    cards_yellow: Optional[int] = None
    cards_red: Optional[int] = None
    touches: Optional[int] = None
    pressures: Optional[int] = None
    tackles: Optional[int] = None
    interceptions: Optional[int] = None
    blocks: Optional[int] = None
    xg: Optional[float] = None
    xa: Optional[float] = None
    sca: Optional[int] = None
    gca: Optional[int] = None
    passes_completed: Optional[int] = None
    passes: Optional[int] = None
    progressive_passes: Optional[int] = None
    dribbles_completed: Optional[int] = None
    dribbles: Optional[int] = None
    fouls: Optional[int] = None
    fouled: Optional[int] = None
    @classmethod
    def get_empty_dict(cls,alias=False):
        fields_list = list(cls.schema(alias).get("properties").keys())
        return dict(zip(fields_list, [None for i in fields_list]))


