"""Script extractor base class."""

from __future__ import annotations

from abc import abstractmethod
import polars as pl
from seinpy.schema import Script
from seinpy.base import Extractor

import logging

logger = logging.getLogger(__name__)


class ScriptExtractor(Extractor):
    """Script extractor base class."""

    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> Script:
        df = self.extract_script(episode_id, episode_num, episode_title)
        return self._df_to_script(df)

    @staticmethod
    def _df_to_script(df: pl.DataFrame) -> Script:
        """Convert a dataframe to a script.

        Args:
            df: The dataframe to convert.

        Returns:
            A script object.
        """
        return df.to_dicts()

    @staticmethod
    def _convert_episodeid_to_episodenum(df: pl.DataFrame) -> pl.DataFrame:
        """Convert the episode id to the episode number.

        Args:
            df: The dataframe to convert.
            col: The column to convert.

        Thr function will convert the episode_id column to a new episode_number col.
        The episode_id is in the format "S01E04", so the function will return 4.
        """
        ranked = (
            df.select("episode_id")
            .unique()
            .sort("episode_id")
            .with_row_index(name="episode_num", offset=1)
        )
        return df.join(ranked, on="episode_id", how="left")

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
            logger.error(
                "Multiple episodes found - episode identifiers are not unique"
            )
            return False
        return True

    @abstractmethod
    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.DataFrame:
        """Extract the script for the given episode to be parsed.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the script for the given episode.
        """
        pass
