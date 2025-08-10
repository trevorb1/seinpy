"""Extract ratings from Open Movie Database.

https://www.omdbapi.com/

This API is free to use, but requires an API key.
https://www.omdbapi.com/apikey.aspx
"""

from seinpy.base import RatingExtractor
import polars as pl
from seinpy.schema import Rating, EpisodeRef
from seinpy.utils import get_episode_filter_priority, METADATA
import logging
import os
import requests

logger = logging.getLogger(__name__)

OMDB_API = "http://www.omdbapi.com/"


class OMDBRatingExtractor(RatingExtractor):
    """Extract ratings from IMDB via OMDB."""

    def __init__(self, omdb_api_key: str | None = None) -> None:
        if omdb_api_key:
            self.omdb_api_key = omdb_api_key
        else:
            self.omdb_api_key = os.getenv("OMDB")
        if self.omdb_api_key is None:
            raise ValueError("OMDB_API_KEY is not set")
        self.api_call = self._get_api_call()

    def _get_api_call(self) -> str:
        """Get the raw data from the Open Movie Database."""
        return f"{OMDB_API}?apikey={self.omdb_api_key}&i="

    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Rating | pl.DataFrame:
        data = self.extract_rating(episode_id, episode_num, episode_title)
        if as_df:
            return pl.DataFrame(data)
        return self._data_to_rating(data)

    def _data_to_rating(self, df: pl.DataFrame) -> Rating:
        """Convert a dataframe to a rating."""
        episode_id = df.select("episode_id").unique().item()
        episode_num = df.select("episode_num").unique().item()
        episode_title = df.select("episode_title").unique().item()
        rating = df.select("rating").unique().item()
        num_votes = df.select("num_votes").unique().item()
        link = df.select("link").unique().item()
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

    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.DataFrame:
        """
        Extract the rating for the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the rating for the given episode.
        """

        priority = get_episode_filter_priority(episode_id, episode_num, episode_title)

        if priority == "episode_id":
            logger.info(f"Extracting rating for episode_id: {episode_id}")
            filtered_df = METADATA.filter(pl.col("episode_id") == episode_id)
        elif priority == "episode_num":
            logger.info(f"Extracting rating for episode_num: {episode_num}")
            filtered_df = METADATA.filter(pl.col("episode_num") == episode_num)
        elif priority == "episode_title":
            logger.info(f"Extracting rating for episode_title: {episode_title}")
            filtered_df = METADATA.filter(pl.col("episode_title") == episode_title)
        else:
            raise ValueError("No episode_id, episode_num, or episode_title provided")

        imdb_id = filtered_df.select("imdb").collect().item()

        response = requests.get(f"{self.api_call}{imdb_id}").json()

        episode_id = (
            episode_id
            if episode_id
            else filtered_df.select("episode_id").collect().item()
        )
        episode_num = (
            episode_num
            if episode_num
            else filtered_df.select("episode_num").collect().item()
        )
        episode_title = (
            episode_title
            if episode_title
            else filtered_df.select("episode_title").collect().item()
        )

        # Pilot episode has differnt name
        if episode_title == "The Seinfeld Chronicles - Pilot":
            episode_title = "Good News, Bad News"

        imdb_link = f"https://www.imdb.com/title/{imdb_id}/"

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
            "rating": float(response["imdbRating"])
            if response["imdbRating"] != "N/A"
            else "",
            "num_votes": int(response["imdbVotes"].replace(",", ""))
            if response["imdbVotes"] != "N/A"
            else "",
            "link": imdb_link,
        }

        return pl.DataFrame(data)
