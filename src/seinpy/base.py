"""Base classes for extractors and writers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union
import polars as pl
import logging
from seinpy.schema import (
    Actor,
    Director,
    Episode,
    EpisodeRef,
    Script,
    Rating,
    Credit,
    ScriptLine,
    Writer,
)

logger = logging.getLogger(__name__)


class ScriptExtractor(ABC):
    """Base strategy class for script extractors."""

    @abstractmethod
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Script | pl.DataFrame:
        """Extract script data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.
            as_df: Whether to return a dataframe or a Script object.

        Returns:
            A Script object or a dataframe.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass

    @staticmethod
    def _df_to_script(df: pl.LazyFrame) -> Script:
        """Convert a dataframe to a script.

        Args:
            df: The dataframe to convert.

        Returns:
            A script object.
        """
        df = df.collect()  # materialize the dataframe once

        episode_id = df.select("episode_id").unique().item()
        episode_num = df.select("episode_num").unique().item()
        episode_title = df.select("episode_title").unique().item()
        ref = EpisodeRef(
            episode_id=episode_id, episode_num=episode_num, episode_title=episode_title
        )

        lines = list(zip(df["speaker"].to_list(), df["dialogue"].to_list()))
        script_lines = [ScriptLine(speaker=line[0], dialogue=line[1]) for line in lines]

        return Script(ref=ref, script_lines=script_lines)

    @staticmethod
    def _convert_episodeid_to_episodenum(df: pl.LazyFrame) -> pl.LazyFrame:
        """Convert the episode id to the episode number.

        Args:
            df: The dataframe to convert.

        This function will convert the episode_id column to a new episode_number col.
        The episode_id is in the format "S01E04", so the function will return 4.
        If the episode_num column already exists, it will be dropped and replaced.
        """
        ranked = (
            df.select("episode_id")
            .unique()
            .sort("episode_id")
            .with_row_index(name="episode_num", offset=1)
        )
        if "episode_num" in df.collect_schema().names():
            return df.drop("episode_num").join(ranked, on="episode_id", how="left")
        else:
            return df.join(ranked, on="episode_id", how="left")

    @staticmethod
    def _is_one_episode(df: pl.LazyFrame) -> bool:
        """Check that only one episode is found.

        Args:
            df: The dataframe to check.
        """
        cols = df.collect_schema().names()
        if not all(
            col in cols for col in ["episode_id", "episode_num", "episode_title"]
        ):
            logger.error(
                f"Missing columns. Expected: ['episode_id', 'episode_num', 'episode_title'] and found: {cols}"
            )
            return False

        unique_counts = df.select(
            [
                pl.col("episode_id").n_unique(),
                pl.col("episode_num").n_unique(),
                pl.col("episode_title").n_unique(),
            ]
        ).collect()

        if any(count != 1 for count in unique_counts.row(0)):
            logger.error(f"Unique counts: {unique_counts}")
            logger.error("Multiple episodes found - episode identifiers are not unique")
            return False
        return True

    @staticmethod
    def _coordinate_columns(df: pl.LazyFrame) -> pl.LazyFrame:
        """Coordinate the columns of the dataframe.

        Args:
            df: The dataframe to coordinate.
        """
        if not all(
            col in df.collect_schema().names()
            for col in [
                "episode_num",
                "episode_title",
                "episode_id",
                "speaker",
                "dialogue",
            ]
        ):
            raise ValueError("Columns are not coordinated")
        return df.select(
            ["episode_num", "episode_title", "episode_id", "speaker", "dialogue"]
        )


class RatingExtractor(ABC):
    """Base strategy class for rating extractors."""

    @abstractmethod
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Rating | pl.DataFrame:
        """Extract rating data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.
            as_df: Whether to return a dataframe or a Rating object.

        Returns:
            A Rating object or a dataframe.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass

    def _df_to_rating(self, df: pl.LazyFrame) -> Rating:
        """Convert a dataframe to a rating."""

        df = df.collect()  # materialize the dataframe once

        episode_id = df.select("episode_id").unique().item()
        episode_num = df.select("episode_num").unique().item()
        episode_title = df.select("episode_title").unique().item()
        rating = df.select("rating").unique().item()
        num_votes = df.select("num_votes").unique().item()
        link = df.select("link").unique().item()
        logger.debug(f"Rating: {rating}")
        logger.debug(f"Num Votes: {num_votes}")
        logger.debug(f"Link: {link}")
        logger.debug(f"Episode ID: {episode_id}")
        logger.debug(f"Episode Num: {episode_num}")
        logger.debug(f"Episode Title: {episode_title}")
        return Rating(
            ref=EpisodeRef(
                episode_id=episode_id,
                episode_num=episode_num,
                episode_title=episode_title,
            ),
            rating=rating,
            num_votes=num_votes,
            link=link,
        )


class CreditExtractor(ABC):
    """Base strategy class for credit extractors."""

    @abstractmethod
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Credit | pl.DataFrame:
        """Extract credit data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.
            as_df: Whether to return a dataframe or a Credit object.

        Returns:
            A Credit object.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass

    @staticmethod
    def _df_to_credits(df: pl.LazyFrame) -> Credit:
        """Convert a dataframe to a credit."""

        df = df.collect()  # materialize the dataframe once

        if len(df) > 1:
            raise ValueError("Multiple episodes found")

        try:
            actor_plus_roles = [
                x.strip() for x in df.select("actors").item().split(";")
            ]

            actors = []
            for actor_plus_role in actor_plus_roles:
                actor = actor_plus_role.split("|")
                if len(actor) == 2:
                    actors.append(Actor(name=actor[0], role=actor[1]))
                else:
                    actors.append(Actor(name=actor[0]))
        except pl.exceptions.ColumnNotFoundError:
            logger.debug("No actors found")
            actors = []

        try:
            writers = []
            for writer in df.select("writer").item().split(";"):
                writers.append(Writer(name=writer))
        except pl.exceptions.ColumnNotFoundError:
            logger.debug("No writers found")
            writers = []

        try:
            directors = []
            for director in df.select("director").item().split(";"):
                directors.append(Director(name=director))
        except pl.exceptions.ColumnNotFoundError:
            logger.debug("No directors found")
            directors = []

        try:
            date = df.select("date").item()
        except pl.exceptions.ColumnNotFoundError:
            logger.debug("No date found")
            date = ""

        try:
            description = df.select("description").item()
        except pl.exceptions.ColumnNotFoundError:
            logger.debug("No description found")
            description = ""

        return Credit(
            ref=EpisodeRef(
                episode_id=df.select("episode_id").item(),
                episode_num=df.select("episode_num").item(),
                episode_title=df.select("episode_title").item(),
            ),
            description=description,
            date=date,
            writers=writers,
            directors=directors,
            actors=actors,
        )


class Exporter(ABC):
    """Base strategy class for all writers."""

    @abstractmethod
    def export(
        self,
        data: Union[List[Episode], List[Script], List[Rating], List[Credit]],
    ) -> None:
        """Write the data to the file.

        Args:
            data: The data to write (episodes, scripts, ratings, or credits).
        """
        pass
