"""Empty credit extractor.

Needed for context when only one extractor is used.
"""

import logging

import polars as pl

from seinpy.base import RatingExtractor
from seinpy.utils import filter_metadata, get_episode_id_num_title

logger = logging.getLogger(__name__)


class EmptyRatingExtractor(RatingExtractor):
    """Empty rating extractor."""

    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the rating from the given episode."""

        logger.warning("No ratings extractor defined, returning empty ratings")

        df = filter_metadata(episode_id, episode_num, episode_title, "empty ratings")

        episode_id, episode_num, episode_title = get_episode_id_num_title(
            df, episode_id, episode_num, episode_title
        )

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
        }

        return pl.LazyFrame(data)
