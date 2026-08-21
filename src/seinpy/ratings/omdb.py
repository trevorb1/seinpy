"""Extract ratings from Open Movie Database.

https://www.omdbapi.com/

This API is free to use, but requires an API key.
https://www.omdbapi.com/apikey.aspx
"""

import logging
from typing import Any

import polars as pl
import requests

from seinpy.base import RatingExtractor
from seinpy.constants import OMDB_API
from seinpy.utils import filter_metadata, get_episode_id_num_title, get_omdb_api_key

logger = logging.getLogger(__name__)


class OMDBRatingExtractor(RatingExtractor):
    """Extract ratings from IMDB via OMDB."""

    def __init__(self, omdb_api_key: str | None = None) -> None:
        self.omdb_api_key = get_omdb_api_key(omdb_api_key)
        self.api_call = self._get_api_call()

    def __eq__(self, other: object) -> bool:
        """Check equality with another OMDBRatingExtractor instance."""
        if not isinstance(other, OMDBRatingExtractor):
            return NotImplemented
        return (
            self.omdb_api_key == other.omdb_api_key and self.api_call == other.api_call
        )

    def _get_api_call(self) -> str:
        """Get the raw data from the Open Movie Database."""
        return f"{OMDB_API}?apikey={self.omdb_api_key}&i="

    @staticmethod
    def convert_rating_2_float(rating: Any) -> float:
        """Convert the rating to a float."""
        if isinstance(rating, str):
            try:
                return float(rating)
            except ValueError:
                logger.warning(f"Invalid rating: {rating}")
            if "." in rating:
                # the rating sometimes comes formatted as xx.xx.xx.xx.xx
                split_rating = ".".join(rating.split(".")[0:2])
                return OMDBRatingExtractor.convert_rating_2_float(split_rating)
            elif rating == "N/A":
                logger.warning("No rating found")
                return 0
            else:
                raise ValueError(f"Invalid rating type: {type(rating)}")
        elif isinstance(rating, (int, float)):
            return rating
        else:
            raise ValueError(f"Invalid rating type: {type(rating)}")

    @staticmethod
    def _correct_episode_titles(title: str) -> str:
        """Correct the episode titles to align with imdb."""
        if title == "The Seinfeld Chronicles - Pilot":
            return "Good News, Bad News"
        return title

    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """
        Extract the rating for the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the rating for the given episode.
        """

        df = filter_metadata(episode_id, episode_num, episode_title, "rating")

        imdb_id = df.select("imdb").collect().item()

        response = requests.get(f"{self.api_call}{imdb_id}").json()

        episode_id, episode_num, episode_title = get_episode_id_num_title(
            df, episode_id, episode_num, episode_title
        )

        episode_title = self._correct_episode_titles(episode_title)

        imdb_link = f"https://www.imdb.com/title/{imdb_id}/"

        rating = response["imdbRating"]
        rating = self.convert_rating_2_float(rating)
        rating *= 10  # imdb rates out of 10, seinpy rates out of 100

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
            "rating": rating if response["imdbRating"] != "N/A" else "",
            "num_votes": int(response["imdbVotes"].replace(",", ""))
            if response["imdbVotes"] != "N/A"
            else "",
            "link": imdb_link,
        }

        return pl.LazyFrame(data)
