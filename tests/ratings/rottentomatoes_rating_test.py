"""Tests for the Rotten Tomatoes rating extractor."""

import pytest

from seinpy.ratings.rottentomatoes import RottenTomatoesRatingExtractor


class TestRottenTomatoesRatingExtractor:
    """Test cases for the RottenTomatoesRatingExtractor class."""

    def test_instantiation_succeeds(self) -> None:
        """Test that instantiating RottenTomatoesRatingExtractor succeeds."""
        extractor = RottenTomatoesRatingExtractor()
        assert isinstance(extractor, RottenTomatoesRatingExtractor)

    def test_extract_raises_not_implemented_error(self) -> None:
        """Test that calling extract raises NotImplementedError."""
        extractor = RottenTomatoesRatingExtractor()
        with pytest.raises(
            NotImplementedError, match="Rotten Tomatoes source not implemented"
        ):
            extractor.extract(episode_id="S01E01")

    def test_read_episodes_raises_not_implemented_error(self, monkeypatch) -> None:
        """Test that read_episodes with Rotten Tomatoes rating source raises NotImplementedError."""
        from seinpy.context import read_episodes
        from seinpy.credits.empty import EmptyCreditExtractor
        from seinpy.scripts.empty import EmptyScriptExtractor

        monkeypatch.setattr(
            EmptyScriptExtractor,
            "extract",
            lambda *a, **k: None,
        )
        monkeypatch.setattr(
            EmptyCreditExtractor,
            "extract",
            lambda *a, **k: None,
        )

        with pytest.raises(
            NotImplementedError, match="Rotten Tomatoes source not implemented"
        ):
            read_episodes(source={"rating": "rottentomatoes"}, episode_ids=["S01E01"])
