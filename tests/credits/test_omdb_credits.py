import pytest
import polars as pl
from seinpy.credits.omdb import OMDBCreditExtractor
from polars.testing import assert_frame_equal

from seinpy.schema import Actor, Credit, Director, EpisodeRef, Writer


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
    def test_extract_credits(self, monkeypatch, fake_df):
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

        fake_response = {
            "Title": "Episode 2",
            "Year": "1990",
            "Rated": "TV-PG",
            "Released": "31 May 1990",
            "Season": "1",
            "Episode": "2",
            "Runtime": "23 min",
            "Genre": "Comedy",
            "Writer": "Larry David, Jerry Seinfeld",
            "Director": "Tom Cherones",
            "Actors": "Jerry Seinfeld, Julia Louis-Dreyfus, Michael Richards, Jason Alexander",
            "Plot": "Seinfeld is literally a show about nothing.",
            "Language": "English",
            "Country": "United States",
            "Awards": "N/A",
            "Poster": "https://m.media-amazon.com/images/M/MV5BNzI4OGU3ODUtYTgxNy00YzZhLWJiODMtMTYyNWNjNGM2YWUzXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
            "Ratings": [{"Source": "Internet Movie Database", "Value": "7.5"}],
            "Metascore": "N/A",
            "imdbRating": "7.5",
            "imdbVotes": "5487",
            "imdbID": "tt0697784",
            "seriesID": "tt0098904",
            "Type": "episode",
            "Response": "True",
        }

        class FakeResponse:
            def json(self):
                return fake_response

        monkeypatch.setattr(
            "seinpy.credits.omdb.requests.get", lambda url: FakeResponse()
        )

        extractor = OMDBCreditExtractor(omdb_api_key="key")
        actual = extractor.extract_credits(episode_id="S01E02")

        expected = fake_df

        assert_frame_equal(actual, expected)

    def test_get_api_call(self):
        extractor = OMDBCreditExtractor(omdb_api_key="key")
        assert extractor._get_api_call() == "http://www.omdbapi.com/?apikey=key&i="

    def test_extract_to_df(self, monkeypatch, fake_df):
        # Mock the extract_credits function
        monkeypatch.setattr(
            "seinpy.credits.omdb.OMDBCreditExtractor.extract_credits",
            lambda *a, **k: fake_df,
        )

        extractor = OMDBCreditExtractor(omdb_api_key="key")
        actual = extractor.extract(episode_id="S01E02", as_df=True)
        expected = fake_df.collect()
        assert_frame_equal(actual, expected)

    def test_extract_to_credit(self, monkeypatch, fake_df):
        # Mock the extract_credits function
        monkeypatch.setattr(
            "seinpy.credits.omdb.OMDBCreditExtractor.extract_credits",
            lambda *a, **k: fake_df,
        )
        extractor = OMDBCreditExtractor(omdb_api_key="key")
        actual = extractor.extract(episode_id="S01E02", as_df=False)
        expected = Credit(
            ref=EpisodeRef(
                episode_id="S01E02",
                episode_num=2,
                episode_title="Episode 2",
            ),
            description="Seinfeld is literally a show about nothing.",
            date="31 May 1990",
            writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
            directors=[Director(name="Tom Cherones")],
            actors=[
                Actor(name="Jerry Seinfeld"),
                Actor(name="Julia Louis-Dreyfus"),
                Actor(name="Michael Richards"),
                Actor(name="Jason Alexander"),
            ],
        )
        assert actual == expected
