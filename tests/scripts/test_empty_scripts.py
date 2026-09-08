import polars as pl
import pytest
from polars.testing import assert_frame_equal

from seinpy.scripts.empty import EmptyScriptExtractor


@pytest.fixture
def fake_df() -> pl.LazyFrame:
    data = {
        "episode_id": "S01E02",
        "episode_num": 2,
        "episode_title": "Episode 2",
    }
    return pl.LazyFrame(data)


class TestEmptyScriptExtractor:
    def test_extract_script(self, monkeypatch, fake_df, metadata):
        monkeypatch.setattr(
            "seinpy.scripts.empty.filter_metadata", lambda *a, **k: metadata
        )

        extractor = EmptyScriptExtractor()
        actual = extractor.extract_script(episode_id="S01E02")
        expected = fake_df
        assert_frame_equal(actual, expected)
