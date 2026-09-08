import polars as pl
import pytest
from polars.testing import assert_frame_equal

from seinpy.credits.omdb import OMDBCreditExtractor


@pytest.fixture
def fake_df() -> pl.LazyFrame:
    data = {
        "episode_id": "S01E02",
        "episode_num": 2,
        "episode_title": "Episode 2",
        "description": "Seinfeld is literally a show about nothing.",
        "date": "31 May 1990",
        "writer": "Larry David; Jerry Seinfeld",
        "director": "Tom Cherones",
        "actors": "Jerry Seinfeld; Julia Louis-Dreyfus; Michael Richards; Jason Alexander",
    }
    return pl.LazyFrame(data)


class TestOMDBCreditExtractor:
    def test_extract_credit(self, monkeypatch, fake_df, fake_omdb_response):
        metadata = pl.DataFrame(
            {
                "imdb": ["tt0697784"],
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2"],
            }
        ).lazy()

        # Mock the filter_metadata function
        monkeypatch.setattr(
            "seinpy.credits.omdb.filter_metadata", lambda *a, **k: metadata
        )

        class FakeResponse:
            def json(self):
                return fake_omdb_response

        monkeypatch.setattr(
            "seinpy.credits.omdb.requests.get", lambda url: FakeResponse()
        )

        extractor = OMDBCreditExtractor(omdb_api_key="key")
        actual = extractor.extract_credit(episode_id="S01E02")

        expected = fake_df

        assert_frame_equal(actual, expected)

    def test_get_api_call(self):
        extractor = OMDBCreditExtractor(omdb_api_key="key")
        assert extractor._get_api_call() == "http://www.omdbapi.com/?apikey=key&i="
