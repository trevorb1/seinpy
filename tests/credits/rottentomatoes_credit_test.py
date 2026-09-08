"""Tests for the Rotten Tomatoes credit extractor."""

import pytest

from seinpy.credits.rottentomatoes import RottenTomatoesCreditExtractor


class TestRottenTomatoesCreditExtractor:
    """Test cases for the RottenTomatoesCreditExtractor class."""

    def test_instantiation_succeeds(self) -> None:
        """Test that instantiating RottenTomatoesCreditExtractor succeeds."""
        extractor = RottenTomatoesCreditExtractor()
        assert isinstance(extractor, RottenTomatoesCreditExtractor)

    def test_extract_raises_not_implemented_error(self) -> None:
        """Test that calling extract raises NotImplementedError."""
        extractor = RottenTomatoesCreditExtractor()
        with pytest.raises(
            NotImplementedError, match="Rotten Tomatoes source not implemented"
        ):
            extractor.extract(episode_id="S01E01")

    def test_read_episodes_raises_not_implemented_error(self, monkeypatch) -> None:
        """Test that read_episodes with Rotten Tomatoes credit source raises NotImplementedError."""
        from seinpy.context import read_episodes
        from seinpy.scripts.empty import EmptyScriptExtractor

        monkeypatch.setattr(
            EmptyScriptExtractor,
            "extract",
            lambda *a, **k: None,
        )

        with pytest.raises(
            NotImplementedError, match="Rotten Tomatoes source not implemented"
        ):
            read_episodes(source={"credit": "rottentomatoes"}, episode_ids=["S01E01"])
