"""Extract seinfeld scripts from kaggle

https://www.kaggle.com/datasets/thec03u5/seinfeld-chronicles and originates from Seinology
"""

from pathlib import Path

from seinpy.schema import Script
from seinpy.scripts.script_extractor import ScriptExtractor

import kagglehub
import polars as pl

import logging

logger = logging.getLogger(__name__)


class KaggleScriptExtractor(ScriptExtractor):
    """Extract scripts from Kaggle."""

    def __init__(self) -> None:
        self.cache_location = None
        self._download_data()
        self.data = self._get_raw_data()

    def _download_data(self) -> None:
        """Download and cache the script from Kaggle.

        Kaggle checks if the dataset is already downloaded.
        """
        self.cache_location = kagglehub.dataset_download("thec03u5/seinfeld-chronicles")

    @staticmethod
    def _adjust_episode_id(df: pl.DataFrame) -> pl.DataFrame:
        """Corrects the episode id.

        The pilot episode and next episode from this dataset are both S01E01.
        This function indexes all season one eisodes by 1 with the exception of the pilot.

        Args:
            df: The dataframe to adjust.

        Returns:
            The adjusted dataframe.
        """

        cols = pl.LazyFrame.collect_schema(df).names()

        # temporary columns
        df = df.with_columns(
            [
                pl.col("episode_id")
                .str.extract(r"S(\d+)E(\d+)", 1)
                .cast(pl.Int32)
                .alias("season"),
                pl.col("episode_id")
                .str.extract(r"S(\d+)E(\d+)", 2)
                .cast(pl.Int32)
                .alias("episode"),
            ]
        )

        # increment only for season 1
        df = df.with_columns(
            pl.when(pl.col("season") == 1)
            .then(
                "S"
                + pl.col("season").cast(str).str.zfill(2)
                + "E"
                + (pl.col("episode") + 1).cast(str).str.zfill(2)
            )
            .otherwise(pl.col("episode_id"))
            .alias("episode_id")
        )
        df = df.select(cols)

        # reset the episode_id for the pilot: "Good News, Bad News"
        return df.with_columns(
            pl.when(pl.col("episode_title") == pl.lit("Good News, Bad News"))
            .then(pl.lit("S01E01"))
            .otherwise(pl.col("episode_id"))
            .alias("episode_id")
        )

    @staticmethod
    def _read_script(data_path: Path) -> pl.DataFrame:
        return (
            pl.scan_csv(Path(data_path, "scripts.csv"))
            .with_columns(
                [pl.col("EpisodeNo").cast(pl.Int8), pl.col("Season").cast(pl.Int8)]
            )
            .rename(
                {
                    "Character": "speaker",
                    "Dialogue": "dialogue",
                    "EpisodeNo": "episode_num",
                    "SEID": "episode_id",
                }
            )
        )

    @staticmethod
    def _read_episode_info(data_path: Path) -> pl.DataFrame:
        return (
            pl.scan_csv(Path(data_path, "episode_info.csv"))
            .with_columns(
                [pl.col("EpisodeNo").cast(pl.Int8), pl.col("Season").cast(pl.Int8)]
            )
            .rename(
                {
                    "EpisodeNo": "episode_num",
                    "SEID": "episode_id",
                    "Title": "episode_title",
                }
            )
        )

    @staticmethod
    def _join_script_and_info(
        episode_info: pl.DataFrame, script: pl.DataFrame
    ) -> pl.DataFrame:
        """Join the script and info files.

        Args:
            episode_info: The raw episode info dataframe.
            script: The raw script dataframe.

        Returns:
            The joined dataframe.
        """
        return episode_info.join(
            script, left_on="episode_id", right_on="episode_id", how="left"
        ).select(["episode_num", "episode_title", "episode_id", "speaker", "dialogue"])

    def _get_raw_data(self) -> pl.DataFrame:
        """Format the raw data.

        This function:
        - Joins the script and info files.
        - Converts the episode_id to a new episode_num column.
        - Adjusts the episode_id for the pilot episode.

        Args:
            None
        """
        script = self._read_script(self.cache_location)
        episode_info = self._read_episode_info(self.cache_location)
        df = self._join_script_and_info(episode_info, script)
        df = self._convert_episodeid_to_episodenum(df)
        return self._adjust_episode_id(df)

    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> Script:
        if episode_id is not None:
            logger.info(f"Extracting script for episode_id: {episode_id}")
            df = self.data.filter(pl.col("episode_id") == episode_id)
        elif episode_num is not None:
            logger.info(f"Extracting script for episode_num: {episode_num}")
            df = self.data.filter(pl.col("episode_num") == episode_num)
        elif episode_title is not None:
            logger.info(f"Extracting script for episode_title: {episode_title}")
            df = self.data.filter(pl.col("episode_title") == episode_title)
        else:
            raise ValueError("No episode_id, episode_num, or episode_title provided")

        # Check that we only have one episode
        if not self._is_unique_counts(df):
            raise ValueError(
                f"Multiple episodes found with: \n"
                f"episode_id: {episode_id} \n"
                f"episode_num: {episode_num} \n"
                f"episode_title: {episode_title}"
            )

        return df.collect()
