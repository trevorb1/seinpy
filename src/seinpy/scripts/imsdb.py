"""Extract scripts from imsbd.com

https://imsdb.com/TV/Seinfeld.html
"""



import polars as pl

from seinpy.base import ScriptExtractor


class IMDbScriptExtractor(ScriptExtractor):
    """IMDb script extractor."""

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
            NotImplementedError: IMDb source not implemented.
        """
        raise NotImplementedError("IMDb source not implemented")
