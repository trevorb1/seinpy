"""Extract ratings from Open Movie Database.

https://www.omdbapi.com/

This API is free to use, but requires an API key.
https://www.omdbapi.com/apikey.aspx

"""

from seinpy.base import RatingExtractor
import polars as pl
from seinpy.schema import Rating, EpisodeRef
from seinpy.utils import get_episode_filter_priority
import logging

logger = logging.getLogger(__name__)


class IMDBRatingExtractor(RatingExtractor):
    """Extract ratings from IMDB."""

    def __init__(self) -> None:
        self.data = self._get_raw_data()

    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
        omdb_api_key: str | None = None,
    ) -> Rating | pl.DataFrame:
        df = self.extract_rating(episode_id, episode_num, episode_title, omdb_api_key)
        if as_df:
            return df
        return self._df_to_rating(df)

    def _df_to_rating(self, df: pl.DataFrame) -> Rating:
        """Convert a dataframe to a rating."""
        episode_id = df.select("episode_id").unique().item()
        episode_num = df.select("episode_num").unique().item()
        episode_title = df.select("episode_title").unique().item()
        rating = df.select("rating").unique().item()
        return Rating(
            ref=EpisodeRef(
                episode_id=episode_id,
                episode_num=episode_num,
                episode_title=episode_title,
            ),
            rating=rating,
        )

    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        omdb_api_key: str | None = None,
    ) -> pl.DataFrame:
        """
        Extract the rating for the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            omdb_api_key: The API key for the Open Movie Database.

        Returns:
            A dataframe with the rating for the given episode.
        """
        
        if omdb_api_key is None:
            raise ValueError("omdb_api_key is required")

        priority = get_episode_filter_priority(episode_id, episode_num, episode_title)

        if priority == "episode_id":
            logger.info(f"Extracting rating for episode_id: {episode_id}")
            df = self.data.filter(pl.col("episode_id") == episode_id)
        elif priority == "episode_num":
            logger.info(f"Extracting rating for episode_num: {episode_num}")
            df = self.data.filter(pl.col("episode_num") == episode_num)
        elif priority == "episode_title":
            logger.info(f"Extracting rating for episode_title: {episode_title}")
            df = self.data.filter(pl.col("episode_title") == episode_title)
        else:
            raise ValueError("No episode_id, episode_num, or episode_title provided")
        
        
