"""Main data schema"""

import logging
import re
from typing import Self

from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)


def capitalize_name(value: str) -> str:
    """Capitalize and clean name."""
    return value.strip().title()


class ScriptLine(BaseModel):
    speaker: str
    dialogue: str

    @field_validator("speaker", mode="after")
    def _capitalize(cls, value: str) -> str:
        return capitalize_name(value)


class Actor(BaseModel):
    name: str
    role: str | None = None

    @field_validator("name", "role", mode="after")
    def _capitalize(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return capitalize_name(value)


class Writer(BaseModel):
    name: str

    @field_validator("name", mode="after")
    def _capitalize(cls, value: str) -> str:
        return capitalize_name(value)


class Director(BaseModel):
    name: str

    @field_validator("name", mode="after")
    def _capitalize(cls, value: str) -> str:
        return capitalize_name(value)


class EpisodeRef(BaseModel):
    episode_id: str | None = None
    episode_num: int | None = None
    episode_title: str | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EpisodeRef):
            return False
        return (
            self.episode_id == other.episode_id
            and self.episode_num == other.episode_num
            and self.episode_title == other.episode_title
        )

    def __str__(self) -> str:
        return f"EpisodeRef: {self.episode_id} (Num: {self.episode_num}, Title: {self.episode_title})"

    def __bool__(self) -> bool:
        """Return True if any of the reference fields are set."""
        return any(
            [
                self.episode_id is not None,
                self.episode_num is not None,
                self.episode_title is not None,
            ]
        )

    @field_validator("episode_title", mode="before")
    @classmethod
    def _validate_episode_title(cls, value: str | None) -> str | None:
        """Capitalize first letter of each word, strip whitespace, and ensure period at end."""
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("episode_title must be a string")
        title = " ".join(word.strip().title() for word in value.split())
        if not any(title.endswith(x) for x in [".", "!", "?"]):
            title += "."
        return title

    @field_validator("episode_id", mode="before")
    @classmethod
    def _validate_episode_id(cls, value: str | None) -> str | None:
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
    script_lines: list[ScriptLine]


class Rating(BaseModel):
    ref: EpisodeRef
    rating: float | None = None
    num_votes: int | None = None
    link: str | None = None

    @field_validator("num_votes", mode="before")
    @classmethod
    def _validate_num_votes(cls, value: int | None) -> int:
        return value if value else 0

    @field_validator("rating", mode="before")
    @classmethod
    def _validate_rating(cls, value: float) -> float:
        if value is None:
            logger.error("No rating found")
            return 0.0
        if not 0 <= value <= 100:
            raise ValueError("rating must be between 0 and 100")
        return round(value, 2)

    @field_validator("link", mode="before")
    @classmethod
    def _validate_link(cls, value: str | None) -> str | None:
        if not value:
            return ""
        if not value.startswith("http"):
            raise ValueError("link must be a valid URL")
        return value


class Credit(BaseModel):
    ref: EpisodeRef
    description: str | None = None
    date: str | None = None
    writers: list[Writer] | None = None
    directors: list[Director] | None = None
    actors: list[Actor] | None = None


class Episode(BaseModel):
    """Episode schema composed of script, rating, and credit data."""

    script: Script | None = None
    rating: Rating | None = None
    credit: Credit | None = None

    @property
    def ref(self) -> EpisodeRef:
        """Get the episode reference from any component that has one."""
        if self.script:
            return self.script.ref
        if self.rating:
            return self.rating.ref
        if self.credit:
            return self.credit.ref
        raise ValueError("No episode reference found")

    @model_validator(mode="after")
    def _validate_metadata(self) -> Self:
        """Validate episode metadata agaisnt one another."""
        refs = {}
        if self.script:
            refs["script"] = self.script.ref
        if self.rating:
            refs["rating"] = self.rating.ref
        if self.credit:
            refs["credit"] = self.credit.ref

        base_component = None
        base_ref = None
        for component, ref in refs.items():
            if not base_ref:  # all of id, num, title are required in validation.
                base_component = component
                base_ref = ref
            else:
                if ref == base_ref:
                    continue
                else:
                    logger.error(f"{component} ref:\n -> {ref}")
                    logger.error(f"{base_component} ref:\n -> {base_ref}")
                    raise ValueError(
                        f"'{base_component}' ref does not match '{component}' ref.\n"
                    )

        return self

    def __str__(self) -> str:
        return f"Episode ID: {self.ref.episode_id}\nEpisode Number: {self.ref.episode_num}\nEpisode Title: {self.ref.episode_title}"
