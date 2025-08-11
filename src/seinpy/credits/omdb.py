"""Extract credits from Open Movie Database.

https://www.omdbapi.com/

This API is free to use, but requires an API key.
https://www.omdbapi.com/apikey.aspx
"""

import polars as pl
from seinpy.base import CreditExtractor
from seinpy.schema import Credit
from seinpy.utils import filter_metadata, get_omdb_api_key
from seinpy.constants import OMDB_API
import logging
import requests

logger = logging.getLogger(__name__)


class OMDBCreditExtractor(CreditExtractor):
    """Extract credits from Open Movie Database."""

    def __init__(self, omdb_api_key: str | None = None) -> None:
        self.omdb_api_key = get_omdb_api_key(omdb_api_key)
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
    ) -> pl.DataFrame | Credit:
        """Extract the credits for the given episode."""
        data = self.extract_credits(episode_id, episode_num, episode_title)
        if as_df:
            return data
        return self._df_to_credits(data)

    def extract_credits(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the credits for the given episode."""

        df = filter_metadata(episode_id, episode_num, episode_title, "credits")

        imdb_id = df.select("imdb").collect().item()

        response = requests.get(f"{self.api_call}{imdb_id}").json()

        episode_id = (
            episode_id if episode_id else df.select("episode_id").collect().item()
        )
        episode_num = (
            episode_num if episode_num else df.select("episode_num").collect().item()
        )
        episode_title = (
            episode_title
            if episode_title
            else df.select("episode_title").collect().item()
        )

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
            "description": response["Plot"],
            "date": response["Released"],
            "writer": response["Writer"],
            "director": response["Director"],
            "actors": response["Actors"],
        }

        return pl.LazyFrame(data)

