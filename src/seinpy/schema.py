"""Main data schema"""

from pydantic import BaseModel, field_validator
from typing import List, Optional
import re


class ScriptLine(BaseModel):
    speaker: str
    dialogue: str

    @field_validator("speaker", mode="after")
    def _capitalize(cls, value: str) -> str:
        return value.strip().title()

class Actor(BaseModel):
    name: str
    role: Optional[str] = None

    @field_validator("name", "role", mode="after")
    def _capitalize(cls, value: str) -> str:
        return value.strip().title()


class EpisodeRef(BaseModel):
    episode_id: str = None
    episode_num: int = None
    episode_title: str = None

    @field_validator("episode_id", mode="before")
    def _validate_episode_id(cls, value: Optional[str]) -> Optional[str]:
        """Ensure episode_id is in the format 'SxxExx'."""
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("episode_id must be a string in the format 'SxxExx'")
        normalized = value.strip().upper()
        if re.fullmatch(r"S\d{2}E\d{2}", normalized) is None:
            raise ValueError("episode_id must be in the format 'SxxExx', e.g. 'S01E02'")
        return normalized


class Script(BaseModel):
    ref: EpisodeRef
    script_lines: List[ScriptLine]


class Rating(BaseModel):
    ref: EpisodeRef
    rating: float
    num_votes: Optional[int] = None
    link: Optional[str] = None


class Credit(BaseModel):
    ref: EpisodeRef
    description: Optional[str] = None
    date: Optional[str] = None
    writer: Optional[List[str]] = None
    director: Optional[List[str]] = None
    actors: Optional[List[Actor]] = None

    @field_validator("writer", "director", mode="after")
    def _capitalize(cls, values: List[str]) -> List[str]:
        return [x.strip().title() for x in values]

class Episode(BaseModel):
    """Episode schema composed of script, rating, and credit data."""

    ref: EpisodeRef
    script: Script
    rating: Rating
    credit: Credit

    # @model_validator(mode="after")
    # def _check_alignment(self):
    #     episode_id = self.episode_id
    #     episode_num = self.episode_num
    #     episode_title = self.episode_title

    #     for part_name in ("script", "rating", "credit"):
    #         part = values.get(part_name)
    #         if part is None:
    #             continue
    #         ref = getattr(part, "ref", None)
    #         if ref is None:
    #             continue
    #         if ref.episode_id is not None and ref.episode_id != eid:
    #             raise ValueError(
    #                 f"{part_name}.ref.episode_id does not match episode_id"
    #             )
    #         if ref.episode_num is not None and ref.episode_num != enum:
    #             raise ValueError(
    #                 f"{part_name}.ref.episode_num does not match episode_num"
    #             )
    #         if ref.episode_title is not None and ref.episode_title != etitle:
    #             raise ValueError(
    #                 f"{part_name}.ref.episode_title does not match episode_title"
    #             )
    #     return values

    def __str__(self):
        return f"Episode: {self.episode_title} (Rating: {self.rating.rating})"
