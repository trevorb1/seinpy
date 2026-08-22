"""Tests for the Seinology script extractor."""

import pytest

from seinpy.scripts.seinology import SeinologyScriptExtractor


class TestSeinologyScriptExtractor:
    """Test cases for the SeinologyScriptExtractor class."""

    def test_instantiation_succeeds(self) -> None:
        """Test that instantiating SeinologyScriptExtractor succeeds."""
        extractor = SeinologyScriptExtractor()
        assert isinstance(extractor, SeinologyScriptExtractor)

    def test_extract_raises_not_implemented_error(self) -> None:
        """Test that calling extract raises NotImplementedError."""
        extractor = SeinologyScriptExtractor()
        with pytest.raises(
            NotImplementedError, match="Seinology source not implemented"
        ):
            extractor.extract(episode_id="S01E01")

    def test_read_episodes_raises_not_implemented_error(self) -> None:
        """Test that read_episodes with Seinology script source raises NotImplementedError."""
        from seinpy.context import read_episodes

        with pytest.raises(
            NotImplementedError, match="Seinology source not implemented"
        ):
            read_episodes(source={"script": "seinology"}, episode_ids=["S01E01"])
