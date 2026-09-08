"""Extract scripts from seinfeldscripts.com

https://www.seinfeldscripts.com/xxx.htm
"""

import polars as pl

from seinpy.base import ScriptExtractor


class SeinfeldScriptsExtractor(ScriptExtractor):
    """SeinfeldScripts extractor."""

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
            NotImplementedError: SeinfeldScripts source not implemented.
        """
        raise NotImplementedError("SeinfeldScripts source not implemented")
