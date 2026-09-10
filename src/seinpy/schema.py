"""Main data schema for Seinfeld episode components."""

import logging
import re
from typing import Self

from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)


def capitalize_name(value: str) -> str:
    """Capitalize and clean a name string.

    Args:
        value: Name string to capitalize and clean.

    Returns:
        Cleaned, title-cased string.
    """
    return value.strip().title()


class ScriptLine(BaseModel):
    """A single line of dialogue spoken by a character in an episode.

    Attributes:
        speaker: Character name speaking the dialogue.
        dialogue: Spoken dialogue text.
    """

    speaker: str
    dialogue: str

    @field_validator("speaker", mode="after")
    def _capitalize(cls, value: str) -> str:
        """Capitalize and clean speaker name."""
        return capitalize_name(value)


class Actor(BaseModel):
    """Actor credit information including actor name and role portrayed.

    Attributes:
        name: Full name of the actor.
        role: Character or role portrayed by the actor, if available.
    """

    name: str
    role: str | None = None

    @field_validator("name", "role", mode="after")
    def _capitalize(cls, value: str | None) -> str | None:
        """Capitalize and clean name and role."""
        if value is None:
            return value
        return capitalize_name(value)


class Writer(BaseModel):
    """Writer credit information for an episode.

    Attributes:
        name: Full name of the writer.
    """

    name: str

    @field_validator("name", mode="after")
    def _capitalize(cls, value: str) -> str:
        """Capitalize and clean writer name."""
        return capitalize_name(value)


class Director(BaseModel):
    """Director credit information for an episode.

    Attributes:
        name: Full name of the director.
    """

    name: str

    @field_validator("name", mode="after")
    def _capitalize(cls, value: str) -> str:
        """Capitalize and clean director name."""
        return capitalize_name(value)


class EpisodeRef(BaseModel):
    """Reference identifiers for a specific episode.

    Attributes:
        episode_id: Episode identifier in 'SxxExx' format (e.g. 'S01E02').
        episode_num: Overall episode number.
        episode_title: Title of the episode.
    """

    episode_id: str | None = None
    episode_num: int | None = None
    episode_title: str | None = None

    def __eq__(self, other: object) -> bool:
        """Check equality against another EpisodeRef instance.

        Args:
            other: Object to compare with.

        Returns:
            True if all reference fields match, False otherwise.
        """
        if not isinstance(other, EpisodeRef):
            return False
        return (
            self.episode_id == other.episode_id
            and self.episode_num == other.episode_num
            and self.episode_title == other.episode_title
        )

    def __str__(self) -> str:
        """Return human-readable representation of episode reference.

        Returns:
            Formatted episode reference string.
        """
        return f"EpisodeRef: {self.episode_id} (Num: {self.episode_num}, Title: {self.episode_title})"

    def __bool__(self) -> bool:
        """Return True if any of the reference fields are set.

        Returns:
            True if at least one reference field is not None.
        """
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
    """Complete episode script comprising dialogue lines and episode reference.

    Attributes:
        ref: Episode reference identifying the episode.
        script_lines: Ordered list of script lines in the episode.
    """

    ref: EpisodeRef
    script_lines: list[ScriptLine]


class Rating(BaseModel):
    """Episode rating details from a rating source.

    Attributes:
        ref: Episode reference identifying the episode.
        rating: Rating score between 0 and 100.
        num_votes: Number of votes or reviews contributing to the rating.
        link: URL linking to the rating page.
    """

    ref: EpisodeRef
    rating: float | None = None
    num_votes: int | None = None
    link: str | None = None

    @field_validator("num_votes", mode="before")
    @classmethod
    def _validate_num_votes(cls, value: int | None) -> int:
        """Default number of votes to 0 if None or empty."""
        return value if value else 0

    @field_validator("rating", mode="before")
    @classmethod
    def _validate_rating(cls, value: float) -> float:
        """Validate and round the episode rating between 0 and 100."""
        if value is None:
            logger.error("No rating found")
            return 0.0
        if not 0 <= value <= 100:
            raise ValueError("rating must be between 0 and 100")
        return round(value, 2)

    @field_validator("link", mode="before")
    @classmethod
    def _validate_link(cls, value: str | None) -> str | None:
        """Validate that the rating link is a valid URL."""
        if not value:
            return ""
        if not value.startswith("http"):
            raise ValueError("link must be a valid URL")
        return value


class Credit(BaseModel):
    """Episode production credits, including air date, cast, and crew.

    Attributes:
        ref: Episode reference identifying the episode.
        description: Brief synopsis or overview of the episode.
        date: Air date of the episode.
        writers: List of credited writers for the episode.
        directors: List of credited directors for the episode.
        actors: List of credited cast members for the episode.
    """

    ref: EpisodeRef
    description: str | None = None
    date: str | None = None
    writers: list[Writer] | None = None
    directors: list[Director] | None = None
    actors: list[Actor] | None = None


class Episode(BaseModel):
    """Episode schema composed of script, rating, and credit data.

    Attributes:
        script: Script data for the episode.
        rating: Rating data for the episode.
        credit: Production credit data for the episode.
    """

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
        """Validate episode metadata against one another."""
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
