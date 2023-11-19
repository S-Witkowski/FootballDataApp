import pydantic
import datetime

from typing import Optional, Union

""" 
Pydantic data model. 
Names of columns should be the same as the names in sql database and the names of the data-stats on website.
"""

class Match(pydantic.BaseModel):
    round: Union[str, None] = None # there is no round for ligue matches
    date: datetime.date
    home: str
    score: str
    away: str
    match_id: str
    season: str
    competition: str
    @classmethod
    def get_empty_dict(cls, alias=False):
        fields_list = list(cls.model_json_schema(alias).get("properties").keys())
        return dict(zip(fields_list, [None for i in fields_list]))

class PlayerStats(pydantic.BaseModel):
    match_id: str
    team: str
    player: str
    player_id: str
    minutes: Union[int, None] = None
    goals: Union[int, None] = None
    assists: Union[int, None] = None
    shots: Union[int, None] = None
    shots_on_target: Union[int, None] = None
    cards_yellow: Union[int, None] = None
    cards_red: Union[int, None] = None
    touches: Union[int, None] = None
    tackles: Union[int, None] = None
    interceptions: Union[int, None] = None
    blocks: Union[int, None] = None
    xg: Union[float, None] = None
    xg_assist: Union[float, None] = None
    sca: Union[int, None] = None
    gca: Union[int, None] = None
    passes_completed: Union[int, None] = None
    passes: Union[int, None] = None
    progressive_passes: Union[int, None] = None
    passes_progressive_distance: Union[int, None] = None
    assisted_shots: Union[int, None] = None
    passes_into_final_third: Union[int, None] = None
    passes_into_penalty_area: Union[int, None] = None
    crosses_into_penalty_area: Union[int, None] = None
    carries: Union[int, None] = None
    progressive_carries: Union[int, None] = None
    carries_distance: Union[int, None] = None
    carries_progressive_distance: Union[int, None] = None
    carries_into_final_third: Union[int, None] = None
    carries_into_penalty_area: Union[int, None] = None
    passes_received: Union[int, None] = None
    progressive_passes_received: Union[int, None] = None
    take_ons: Union[int, None] = None
    take_ons_won: Union[int, None] = None
    fouls: Union[int, None] = None
    fouled: Union[int, None] = None
    @classmethod
    def get_empty_dict(cls,alias=False):
        fields_list = list(cls.model_json_schema(alias).get("properties").keys())
        return dict(zip(fields_list, [None for i in fields_list]))


