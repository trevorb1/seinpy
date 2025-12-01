import pytest
import polars as pl
from seinpy.credits.empty import EmptyCreditExtractor
from polars.testing import assert_frame_equal

@pytest.fixture
def fake_df() -> pl.LazyFrame:
    data = {
        "episode_id": "S01E02",
        "episode_num": 2,
        "episode_title": "Episode 2",
    }
    return pl.LazyFrame(data)

class TestEmptyCreditExtractor:
    def test_extract_credit(self, monkeypatch, fake_df, metadata):
        monkeypatch.setattr(
            "seinpy.credits.empty.filter_metadata", lambda *a, **k: metadata
        )

        extractor = EmptyCreditExtractor()
        actual = extractor.extract_credit(episode_id="S01E02")
        expected = fake_df
        assert_frame_equal(actual, expected)