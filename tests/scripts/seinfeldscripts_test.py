"""Tests for the SeinfeldScripts extractor."""

import pytest

from seinpy.scripts.seinfeldscripts import SeinfeldScriptsExtractor


class TestSeinfeldScriptsExtractor:
    """Test cases for the SeinfeldScriptsExtractor class."""

    def test_instantiation_succeeds(self) -> None:
        """Test that instantiating SeinfeldScriptsExtractor succeeds."""
        extractor = SeinfeldScriptsExtractor()
        assert isinstance(extractor, SeinfeldScriptsExtractor)

    def test_extract_raises_not_implemented_error(self) -> None:
        """Test that calling extract raises NotImplementedError."""
        extractor = SeinfeldScriptsExtractor()
        with pytest.raises(
            NotImplementedError, match="SeinfeldScripts source not implemented"
        ):
            extractor.extract(episode_id="S01E01")

    def test_read_episodes_raises_not_implemented_error(self) -> None:
        """Test that read_episodes with SeinfeldScripts script source raises NotImplementedError."""
        from seinpy.context import read_episodes

        with pytest.raises(
            NotImplementedError, match="SeinfeldScripts source not implemented"
        ):
            read_episodes(source={"script": "seinfeldscripts"}, episode_ids=["S01E01"])
