"""Extract seinfeld scripts from kaggle

https://www.kaggle.com/datasets/thec03u5/seinfeld-chronicles and originates from Seinology
"""

import logging
from pathlib import Path

import kagglehub
import polars as pl

from seinpy.base import ScriptExtractor
from seinpy.constants import TWO_PART_EPISODES
from seinpy.utils import (
    filter_metadata,
    get_episode_id_num_title,
    shift_episode_ids,
    shift_episode_nums,
)

logger = logging.getLogger(__name__)

# The Kaggle dataset merges the pilot ("Good News, Bad News") and episode 2
# ("The Stakeout") into a single continuous block of 557 lines labeled S01E01.
# The pilot concludes at line 211, and line 212 begins "The Stakeout".
PILOT_SCRIPT_LINE_COUNT = 211


class KaggleScriptExtractor(ScriptExtractor):
    """Extract scripts from Kaggle."""

    def __init__(self) -> None:
        self.zip_folder = self._download_data()
        self.data = self._get_raw_data()
        logger.info("Loaded Kaggle Seinfeld episodes")

    def __eq__(self, other: object) -> bool:
        """Check equality with another KaggleScriptExtractor instance."""
        if not isinstance(other, KaggleScriptExtractor):
            return NotImplemented
        return self.zip_folder == other.zip_folder and self.data.equals(other.data)

    ###
    # Downloader
    ###

    def _download_data(self) -> str:
        """Download and cache the script from Kaggle.

        Kaggle checks if the dataset is already downloaded.

        Returns:
            The path to the zip folder.
        """
        zip_folder = kagglehub.dataset_download("thec03u5/seinfeld-chronicles")
        logger.debug(f"Downloaded Kaggle Seinfeld episodes to {zip_folder}")
        return zip_folder

    ###
    # Getters
    ###

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

        df = filter_metadata(episode_id, episode_num, episode_title, "rating")

        episode_id, episode_num, episode_title = get_episode_id_num_title(
            df, episode_id, episode_num, episode_title
        )

        df = self.data.filter(pl.col("episode_id") == episode_id)

        # Check that we only have one episode
        if not self._is_one_episode(df):
            raise ValueError(
                f"Multiple episodes found with: \n"
                f"episode_id: {episode_id} \n"
                f"episode_num: {episode_num} \n"
                f"episode_title: {episode_title}"
            )

        return df

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
            .pipe(self._correct_2_part_episodes)
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

    ###
    # Script processing
    ###

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
            .pipe(self._correct_script_pilot_episode_id)
        )

    ###
    # Info processing
    ###

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
            .pipe(self._correct_pilot_episode_id)  # adjust pilot episode
            .pipe(self._adjust_episode_num)
        )

    ###
    # Helpers
    ###

    @staticmethod
    def _correct_2_part_episodes(df: pl.LazyFrame) -> pl.LazyFrame:
        """Corrects the episode number and ids for 2 part episodes.

        Args:
            df: The dataframe to correct.

        Returns:
            The corrected dataframe.
        """

        # Remove part numbers from episode titles (e.g. " (1)", " (2)")
        df = df.with_columns(pl.col("episode_title").str.replace(r" \(\d+\)$", ""))

        for two_part_episode in TWO_PART_EPISODES:
            episode_id = two_part_episode["episode_id"]
            episode_num = two_part_episode["episode_num"]

            df = shift_episode_ids(df, episode_id).pipe(shift_episode_nums, episode_num)

        return df

    @staticmethod
    def _extract_season_and_episode(
        df: pl.LazyFrame,
        season_col: str = "season_num",
        episode_col: str = "ep_num",
    ) -> pl.LazyFrame:
        """Extracts season and episode numbers from the episode_id column.

        Args:
            df: The dataframe containing an episode_id column.
            season_col: The column name for the extracted season number.
                Defaults to "season_num".
            episode_col: The column name for the extracted episode number.
                Defaults to "ep_num".

        Returns:
            The dataframe with the season and episode columns added.
        """
        return df.with_columns(
            [
                pl.col("episode_id")
                .str.extract(r"S(\d+)E(\d+)", 1)
                .cast(pl.Int32)
                .alias(season_col),
                pl.col("episode_id")
                .str.extract(r"S(\d+)E(\d+)", 2)
                .cast(pl.Int32)
                .alias(episode_col),
            ]
        )

    @staticmethod
    def _increment_season_one_id(
        df: pl.LazyFrame,
        season_col: str = "season_num",
        episode_col: str = "ep_num",
    ) -> pl.LazyFrame:
        """Increments the episode ID by 1 for all Season 1 episodes.

        Args:
            df: The dataframe containing season, episode, and episode_id columns.
            season_col: The column name for the season number.
                Defaults to "season_num".
            episode_col: The column name for the episode number.
                Defaults to "ep_num".

        Returns:
            The dataframe with updated episode_id values for Season 1.
        """
        return df.with_columns(
            pl.when(pl.col(season_col) == 1)
            .then(
                "S"
                + pl.col(season_col).cast(str).str.zfill(2)
                + "E"
                + (pl.col(episode_col) + 1).cast(str).str.zfill(2)
            )
            .otherwise(pl.col("episode_id"))
            .alias("episode_id")
        )

    @staticmethod
    def _increment_season_one_num(
        df: pl.LazyFrame,
        season_col: str = "season_num",
        episode_num_col: str = "episode_num",
    ) -> pl.LazyFrame:
        """Increments the episode number by 1 for all Season 1 episodes.

        Args:
            df: The dataframe containing season and episode number columns.
            season_col: The column name for the season number.
                Defaults to "season_num".
            episode_num_col: The column name for the episode number.
                Defaults to "episode_num".

        Returns:
            The dataframe with updated episode_num values for Season 1.
        """
        return df.with_columns(
            pl.when(pl.col(season_col) == 1)
            .then(pl.col(episode_num_col) + 1)
            .otherwise(pl.col(episode_num_col))
            .alias(episode_num_col)
        )

    def _correct_pilot_episode_id(self, df: pl.LazyFrame) -> pl.LazyFrame:
        """Corrects the episode id.

        The pilot episode and next episode from this dataset are both S01E01.
        This function indexes all season one eisodes by 1 with the exception 
        of the pilot.

        Args:
            df: The dataframe to adjust.

        Returns:
            The adjusted dataframe.
        """

        cols = pl.LazyFrame.collect_schema(df).names()

        # temporary columns
        df = self._extract_season_and_episode(df)

        # increment only for season 1
        df = self._increment_season_one_id(df)
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
        if isinstance(pilot, pl.LazyFrame):
            assert pilot.select("episode_num").collect().height == 1
        else:
            assert pilot.select("episode_num").height == 1

        df = df.with_columns(
            pl.when(pl.col("episode_id") == pl.lit("S01E01"))
            .then(pl.lit(0))  # change from 1 to 0
            .otherwise(pl.col("episode_num"))
            .alias("episode_num")
        )

        return df.with_columns((pl.col("episode_num") + 1).alias("episode_num"))

    def _correct_script_pilot_episode_id(self, df: pl.LazyFrame) -> pl.LazyFrame:
        """Corrects the episode ID and number for the scripts.

        The pilot episode and next episode from this dataset are both S01E01.
        This function splits them and adjusts the episode IDs and numbers accordingly.

        Args:
            df: The script dataframe to adjust.

        Returns:
            The adjusted script dataframe.
        """
        # Add a cumulative count to split on line number 
        df = df.with_columns(
            (pl.col("episode_id") == "S01E01").cum_sum().alias("s1e1_count")
        )
        df = self._extract_season_and_episode(df)

        # In the full dataset S01E01 has 557 lines and the
        # pilot is the first PILOT_SCRIPT_LINE_COUNT lines. For smaller
        # subsets/mock fixtures, split in half.
        split_idx = (
            pl.when(pl.col("s1e1_count").max() > PILOT_SCRIPT_LINE_COUNT)
            .then(PILOT_SCRIPT_LINE_COUNT)
            .otherwise(pl.col("s1e1_count").max() // 2)
        )

        # Set pilot episode numbers to 0
        df = df.with_columns(
            [
                pl.when(
                    (pl.col("season_num") == 1)
                    & (pl.col("s1e1_count") <= split_idx)
                )
                .then(0)
                .otherwise(pl.col("ep_num"))
                .alias("ep_num"),
                pl.when(
                    (pl.col("season_num") == 1)
                    & (pl.col("s1e1_count") <= split_idx)
                )
                .then(0)
                .otherwise(pl.col("episode_num"))
                .alias("episode_num"),
            ]
        )

        # Increment episode number by 1 for all Season 1 episodes
        df = self._increment_season_one_num(df)

        # Increment episode ID by 1 for all Season 1 episodes
        df = self._increment_season_one_id(df)

        # Drop temporary columns
        return df.drop(["s1e1_count", "season_num", "ep_num"])
