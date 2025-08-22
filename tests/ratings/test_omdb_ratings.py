import pytest
import polars as pl
from seinpy.ratings.omdb import OMDBRatingExtractor
from polars.testing import assert_frame_equal

from seinpy.schema import EpisodeRef, Rating


@pytest.fixture
def fake_df() -> pl.LazyFrame:
    data = {
        "episode_id": "S01E02",
        "episode_num": 2,
        "episode_title": "Episode 2",
        "rating": 75.0,
        "num_votes": 5487,
        "link": "https://www.imdb.com/title/tt0697784/",
    }
    return pl.LazyFrame(data)


class TestOMDBRatingExtractor:
    def test_get_api_call(self):
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        assert extractor._get_api_call() == "http://www.omdbapi.com/?apikey=key&i="

    @pytest.mark.parametrize(
        "rating, expected",
        [
            ("7.5", 7.5),
            ("7.5.5.5.5", 7.5),
            ("N/A", 0),
            (7.5, 7.5),
            (7, 7),
        ],
    )
    def test_convert_rating_2_float_valid(
        self, rating: str | int | float, expected: float
    ):
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        assert extractor.convert_rating_2_float(rating) == expected

    @pytest.mark.parametrize(
        "rating, expected",
        [
            ("", 0),
            (None, 0),
        ],
    )
    def test_convert_rating_2_float_invalid(
        self, rating: str | int | float, expected: float
    ):
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        with pytest.raises(ValueError):
            extractor.convert_rating_2_float(rating)

    def test_correct_episode_titles(self):
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        assert (
            extractor._correct_episode_titles("The Seinfeld Chronicles - Pilot")
            == "Good News, Bad News"
        )
        assert extractor._correct_episode_titles("Episode 2") == "Episode 2"

    def test_extract_ratings(self, monkeypatch, fake_df, fake_omdb_response):
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
            "seinpy.ratings.omdb.filter_metadata", lambda *a, **k: metadata
        )

        class FakeResponse:
            def json(self):
                return fake_omdb_response

        monkeypatch.setattr(
            "seinpy.ratings.omdb.requests.get", lambda url: FakeResponse()
        )

        extractor = OMDBRatingExtractor(omdb_api_key="key")
        expected = fake_df

        actual = extractor.extract_rating(
            episode_id="S01E02",
            episode_num=2,
            episode_title="Episode 2",
        )
        assert_frame_equal(actual, expected)

        actual = extractor.extract_rating(
            episode_id="S01E02",
        )
        assert_frame_equal(actual, expected)

    def test_extract_to_df(self, monkeypatch, fake_df):
        # Mock the extract_rating function
        monkeypatch.setattr(
            "seinpy.ratings.omdb.OMDBRatingExtractor.extract_rating",
            lambda *a, **k: fake_df,
        )

        extractor = OMDBRatingExtractor(omdb_api_key="key")
        actual = extractor.extract(episode_id="S01E02", as_df=True)
        assert_frame_equal(actual, fake_df)

    def test_extract_to_rating(self, monkeypatch, fake_df):
        # Mock the extract_rating function
        monkeypatch.setattr(
            "seinpy.ratings.omdb.OMDBRatingExtractor.extract_rating",
            lambda *a, **k: fake_df,
        )
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        actual = extractor.extract(episode_id="S01E02", as_df=False)
        expected = Rating(
            ref=EpisodeRef(
                episode_id="S01E02", episode_num=2, episode_title="Episode 2"
            ),
            rating=75.0,
            num_votes=5487,
            link="https://www.imdb.com/title/tt0697784/",
        )
        assert actual == expected
