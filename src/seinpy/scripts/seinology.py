"""Extract seinology from seinology.com

https://web.archive.org/web/20051212023145/http://www.seinology.com/scripts-english.shtml#sub
"""

import polars as pl

from seinpy.base import ScriptExtractor


class SeinologyScriptExtractor(ScriptExtractor):
    """Seinology script extractor."""

    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        """Extract the script from the given episode.

        Args:
            episode_id: The id of the episode to extract.
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.

        Returns:
            The script dataframe.

        Raises:
            NotImplementedError: Seinology source not implemented.
        """
        raise NotImplementedError("Seinology source not implemented")
