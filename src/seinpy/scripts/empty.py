"""Empty script extractor.

Needed for context when only one extractor is used.
"""

import logging

import polars as pl

from seinpy.base import ScriptExtractor
from seinpy.utils import filter_metadata, get_episode_id_num_title

logger = logging.getLogger(__name__)

class EmptyScriptExtractor(ScriptExtractor):
    """Empty script extractor."""

    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the script from the given episode."""

        logger.warning("No script extractor defined, returning empty script")

        df = filter_metadata(episode_id, episode_num, episode_title, "empty scripts")

        episode_id, episode_num, episode_title = get_episode_id_num_title(
            df, episode_id, episode_num, episode_title
        )

        data = {
            "episode_id": episode_id,
            "episode_num": episode_num,
            "episode_title": episode_title,
        }

        return pl.LazyFrame(data)
