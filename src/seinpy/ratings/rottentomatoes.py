"""Extract ratings from Rotten Tomatoes."""

import polars as pl

from seinpy.base import RatingExtractor


class RottenTomatoesRatingExtractor(RatingExtractor):
    """Rotten Tomatoes rating extractor."""

    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the rating from the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            A dataframe with the rating for the given episode.

        Raises:
            NotImplementedError: Rotten Tomatoes source not implemented.
        """
        raise NotImplementedError("Rotten Tomatoes source not implemented")
