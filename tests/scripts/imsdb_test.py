"""Tests for the IMDb script extractor."""

import pytest

from seinpy.scripts.imsdb import IMDbScriptExtractor


class TestIMDbScriptExtractor:
    """Test cases for the IMDbScriptExtractor class."""

    def test_instantiation_succeeds(self) -> None:
        """Test that instantiating IMDbScriptExtractor succeeds."""
        extractor = IMDbScriptExtractor()
        assert isinstance(extractor, IMDbScriptExtractor)

    def test_extract_raises_not_implemented_error(self) -> None:
        """Test that calling extract raises NotImplementedError."""
        extractor = IMDbScriptExtractor()
        with pytest.raises(NotImplementedError, match="IMDb source not implemented"):
            extractor.extract(episode_id="S01E01")

    def test_read_episodes_raises_not_implemented_error(self) -> None:
        """Test that read_episodes with IMDb script source raises NotImplementedError."""
        from seinpy.context import read_episodes

        with pytest.raises(NotImplementedError, match="IMDb source not implemented"):
            read_episodes(source={"script": "imdb"}, episode_ids=["S01E01"])
