"""Extract seinfeld scripts from kaggle

https://www.kaggle.com/datasets/thec03u5/seinfeld-chronicles and originates from Seinology
"""

from pathlib import Path

from seinpy.schema import Script
from seinpy.base import ScriptExtractor
from seinpy.utils import get_episode_filter_priority

import kagglehub
import polars as pl

import logging

logger = logging.getLogger(__name__)


class KaggleScriptExtractor(ScriptExtractor):
    """Extract scripts from Kaggle."""

    def __init__(self) -> None:
        self.zip_folder = self._download_data()
        self.data = self._get_raw_data()
        logger.info("Loaded Kaggle Seinfeld episodes")

    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Script | pl.DataFrame:
        df = self.extract_script(episode_id, episode_num, episode_title)
        if as_df:
            return df.collect()
        return self._df_to_script(df)

    def _download_data(self) -> str:
        """Download and cache the script from Kaggle.

        Kaggle checks if the dataset is already downloaded.

        Returns:
            The path to the zip folder.
        """
        zip_folder = kagglehub.dataset_download("thec03u5/seinfeld-chronicles")
        logger.debug(f"Downloaded Kaggle Seinfeld episodes to {zip_folder}")
        return zip_folder

    def _get_raw_data(self) -> pl.DataFrame:
        """Format the raw data.

        This function:
        - Joins the script and info files.
        - Converts the episode_id to a new episode_num column.
        - Adjusts the episode_id for the pilot episode.

        Args:
            None
        """
        script = self._read_script()
        episode_info = self._read_episode_info()
        return (
            self._join_script_and_info(episode_info, script)
            .pipe(self._convert_episodeid_to_episodenum)
            .pipe(self._adjust_episode_id)
            .pipe(self._adjust_episode_num)
        )

    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the script for the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            The script dataframe.

        Raises:
            ValueError: If no episode_id, episode_num, or episode_title is provided.
        """
        priority = get_episode_filter_priority(episode_id, episode_num, episode_title)

        if priority == "episode_id":
            logger.info(f"Extracting script for episode_id: {episode_id}")
            df = self.data.filter(pl.col("episode_id") == episode_id)
        elif priority == "episode_num":
            logger.info(f"Extracting script for episode_num: {episode_num}")
            df = self.data.filter(pl.col("episode_num") == episode_num)
        elif priority == "episode_title":
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

        return df

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
    def _adjust_episode_num(df: pl.LazyFrame) -> pl.LazyFrame:
        """Corrects the episode number.

        The pilot episode and the next episode from this dataset are both num 1.
        This function assumes that the S01E01 duplicate has been corrected.

        Args:
            df: The dataframe to adjust.

        Returns:
            The adjusted dataframe.
        """

        # ensure only one S01E01 exists
        pilot = df.filter(pl.col("episode_id") == pl.lit("S01E01"))
        assert pilot.select("episode_num").unique().collect().height == 1

        df = df.with_columns(
            pl.when(pl.col("episode_id") == pl.lit("S01E01"))
            .then(pl.lit(0))  # change from 1 to 0
            .otherwise(pl.col("episode_num"))
            .alias("episode_num")
        )

        return df.with_columns((pl.col("episode_num") + 1).alias("episode_num"))

    def _read_script(self) -> pl.LazyFrame:
        """Read the script file.

        Returns:
            The script dataframe.
        """
        return (
            pl.scan_csv(Path(self.zip_folder, "scripts.csv"))
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

    def _read_episode_info(self) -> pl.LazyFrame:
        """Read the episode info file.

        Returns:
            The episode info dataframe.
        """
        return (
            pl.scan_csv(Path(self.zip_folder, "episode_info.csv"))
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
        episode_info: pl.LazyFrame, script: pl.LazyFrame
    ) -> pl.LazyFrame:
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
