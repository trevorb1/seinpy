"""Base classes for extractors and writers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union
import polars as pl
import logging
from seinpy.schema import Episode, EpisodeRef, Script, Rating, Credit, ScriptLine

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
    def _df_to_script(df: pl.DataFrame) -> Script:
        """Convert a dataframe to a script.

        Args:
            df: The dataframe to convert.

        Returns:
            A script object.
        """
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
    def _convert_episodeid_to_episodenum(df: pl.DataFrame) -> pl.DataFrame:
        """Convert the episode id to the episode number.

        Args:
            df: The dataframe to convert.

        This function will convert the episode_id column to a new episode_number col.
        The episode_id is in the format "S01E04", so the function will return 4.
        """
        ranked = (
            df.select("episode_id")
            .unique()
            .sort("episode_id")
            .with_row_index(name="episode_num", offset=1)
        )
        return df.drop("episode_num").join(ranked, on="episode_id", how="left")

    @staticmethod
    def _is_unique_counts(df: pl.DataFrame) -> bool:
        """Check that the episode identifiers are unique.

        Args:
            df: The dataframe to check.
        """
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
    def _coordinate_columns(df: pl.DataFrame) -> pl.DataFrame:
        """Coordinate the columns of the dataframe.

        Args:
            df: The dataframe to coordinate.
        """
        if not all(
            col in df.columns
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
    ) -> Rating:
        """Extract rating data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.

        Returns:
            A Rating object.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass


class CreditExtractor(ABC):
    """Base strategy class for credit extractors."""

    @abstractmethod
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> Credit:
        """Extract credit data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.

        Returns:
            A Credit object.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass


class Writer(ABC):
    """Base strategy class for all writers."""

    @abstractmethod
    def write(
        self,
        data: Union[List[Episode], List[Script], List[Rating], List[Credit]],
    ) -> None:
        """Write the data to the file.

        Args:
            data: The data to write (episodes, scripts, ratings, or credits).
        """
        pass
