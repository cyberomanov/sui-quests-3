from typing import List, Optional

from pydantic import BaseModel


class Metadata(BaseModel):
    FIRST_APPEARANCE_CHECKPOINT: int
    WORLDS_BEYOND: float
    PANZERDOG: float
    RUN_LEGENDS: float
    BUSHI: float
    ARCADE_CHAMPION: float
    THE_COLLECTION: float
    POETRY_IN_MOTION: float
    SUILETTE: float
    DESUICOINFLIP: float
    HAS_SUINS: bool
    ENGAGEMENT_MULTIPLIER: int
    PASS_ID: Optional[str]
    REFERRAL_POINTS_ELIGIBLE_SUM: float
    REFERRAL_POINTS: float
    IS_ELIGIBLE: bool
    RANK: Optional[str]
    appsUsed: List[str]


class Info(BaseModel):
    address: Optional[str]
    metadata: Optional[Metadata]
    rank: Optional[int]
    reward: Optional[int]
    score: Optional[int]
    bullsharks: Optional[List[str]]
    capys: Optional[List[str]]
    bot: Optional[bool]


class Data(BaseModel):
    data: Optional[Info]


class LeaderboardResponse(BaseModel):
    result: Data
