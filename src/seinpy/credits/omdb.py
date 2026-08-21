"""Extract credits from Open Movie Database.

https://www.omdbapi.com/

This API is free to use, but requires an API key.
https://www.omdbapi.com/apikey.aspx
"""

import logging

import polars as pl
import requests

from seinpy.base import CreditExtractor
from seinpy.constants import OMDB_API
from seinpy.schema import Credit
from seinpy.utils import filter_metadata, get_episode_id_num_title, get_omdb_api_key

logger = logging.getLogger(__name__)


class OMDBCreditExtractor(CreditExtractor):
    """Extract credits from Open Movie Database."""

    def __init__(self, omdb_api_key: str | None = None) -> None:
        self.omdb_api_key = get_omdb_api_key(omdb_api_key)
        self.api_call = self._get_api_call()

    def __eq__(self, other: object) -> bool:
        """Check equality with another OMDBCreditExtractor instance."""
        if not isinstance(other, OMDBCreditExtractor):
            return NotImplemented
        return (
            self.omdb_api_key == other.omdb_api_key and self.api_call == other.api_call
        )

    def _get_api_call(self) -> str:
        """Get the raw data from the Open Movie Database."""
        return f"{OMDB_API}?apikey={self.omdb_api_key}&i="

    def extract_credit(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the credits for the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the credits for the given episode.
        """

        df = filter_metadata(episode_id, episode_num, episode_title, "credits")

        episode_id, episode_num, episode_title = get_episode_id_num_title(
            df, episode_id, episode_num, episode_title
        )

        imdb_id = df.select("imdb").collect().item()
        response = requests.get(f"{self.api_call}{imdb_id}").json()

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
            "description": response["Plot"].replace(",", ";"),
            "date": response["Released"].replace(",", ";"),
            "writer": response["Writer"].replace(",", ";"),
            "director": response["Director"].replace(",", ";"),
            "actors": response["Actors"].replace(",", ";"),
        }

        return pl.LazyFrame(data)
