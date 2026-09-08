import polars as pl
import pytest
from polars.testing import assert_frame_equal

from seinpy.ratings.empty import EmptyRatingExtractor


@pytest.fixture
def fake_df() -> pl.LazyFrame:
    data = {
        "episode_id": "S01E02",
        "episode_num": 2,
        "episode_title": "Episode 2",
    }
    return pl.LazyFrame(data)


class TestEmptyRatingExtractor:
    def test_extract_rating(self, monkeypatch, fake_df, metadata):
        monkeypatch.setattr(
            "seinpy.ratings.empty.filter_metadata", lambda *a, **k: metadata
        )

        extractor = EmptyRatingExtractor()
        actual = extractor.extract_rating(episode_id="S01E02")
        expected = fake_df
        assert_frame_equal(actual, expected)
