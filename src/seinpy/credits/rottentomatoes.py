"""Extract credits from Rotten Tomatoes."""

import polars as pl

from seinpy.base import CreditExtractor


class RottenTomatoesCreditExtractor(CreditExtractor):
    """Rotten Tomatoes credit extractor."""

    def extract_credit(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the credit from the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the credit for the given episode.

        Raises:
            NotImplementedError: Rotten Tomatoes source not implemented.
        """
        raise NotImplementedError("Rotten Tomatoes source not implemented")
