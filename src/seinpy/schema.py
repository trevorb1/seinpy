"""Main data schema"""

from pydantic import BaseModel
from typing import List, Optional


class ScriptLine(BaseModel):
    speaker: str
    dialogue: str


class Episode(BaseModel):
    title: str
    date: str
    episode: str
    season: str
    episode_number: int
    season_number: int
    episode_title: str
    episode_description: str
    script_raw: str
    script_lines: List[ScriptLine]

    def __str__(self):
        return f"{self.title}\n{self.lines}"


class Script(BaseModel):
    episode_title: Optional[str]
    episode_num: Optional[str]
    episode_id: Optional[str]
    script_raw: str
    script_lines: List[ScriptLine]

    def __str__(self):
        return f"{self.title}\n{self.lines}"


class Rating(BaseModel):
    title: str | None
    season: str | None
    episode_number: int
    rating: float


class Credit(BaseModel):
    title: str
    date: str
    episode: str
    season: str
    writer: List[str]
    director: List[str]
