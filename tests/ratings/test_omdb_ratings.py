"""Tests for the OMDB rating extractor module."""

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from seinpy.ratings.omdb import OMDBRatingExtractor
from seinpy.schema import EpisodeRef, Rating


@pytest.fixture
def fake_df() -> pl.LazyFrame:
    """Fixture returning a mock LazyFrame for an episode rating."""
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
    """Tests for OMDBRatingExtractor."""

    def test_get_api_call(self):
        """Test API call URL generation with API key."""
        extractor = OMDBRatingExtractor(omdb_api_key="key")
        assert extractor._get_api_call() == "http://www.omdbapi.com/?apikey=key&i="

    @pytest.mark.parametrize(
        "response, expected",
        [
            (
                {"imdbRating": "7.5", "Ratings": [], "Metascore": "N/A"},
                "7.5",
            ),
            (
                {
                    "imdbRating": "N/A",
                    "Ratings": [{"Source": "Internet Movie Database", "Value": "8.0"}],
                    "Metascore": "N/A",
                },
                "8.0",
            ),
            (
                {"imdbRating": "N/A", "Ratings": [], "Metascore": "85"},
                "85",
            ),
            (
                {"imdbRating": "N/A", "Ratings": [], "Metascore": "N/A"},
                0,
            ),
        ],
    )
    def test_get_rating(self, response: dict, expected: str | int):
        """Test _get_rating extracts rating from imdbRating, Ratings, Metascore, or returns 0.

        Args:
            response: Mocked OMDB response dictionary.
            expected: Expected rating output.
        """
        assert OMDBRatingExtractor._get_rating(response) == expected

    def test_get_rating_no_rating_logs_error(self, caplog):
        """Test _get_rating logs an error when no rating is found.

        Args:
            caplog: Pytest fixture to capture log records.
        """
        response = {"imdbRating": "N/A", "Ratings": [], "Metascore": "N/A"}
        with caplog.at_level("ERROR"):
            result = OMDBRatingExtractor._get_rating(response)
        assert result == 0
        assert "No rating found" in caplog.text

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
