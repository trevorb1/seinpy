from typing import List, Union
from pytest import fixture
import polars as pl
from seinpy.base import Exporter, ScriptExtractor, CreditExtractor, RatingExtractor
from seinpy.schema import Credit, Episode, Rating, Script, EpisodeRef, ScriptLine


@fixture
def metadata() -> pl.LazyFrame:
    """Metadata for the Seinfeld scripts."""
    return pl.LazyFrame(
        {
            "episode_title": [
                "Episode 1",
                "Episode 2",
                "Episode 3",
                "Episode 33",
                "Episode 34",
            ],
            "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
            "episode_num": [1, 2, 3, 33, 34],
            "imdb": ["tt0098286", "tt0697784", "tt0697768", "tt0697698", "tt0697738"],
        }
    )


@fixture
def episode_reference() -> pl.LazyFrame:
    """Metadata for the Seinfeld scripts with season 2."""
    return pl.LazyFrame(
        {
            "episode_title": [
                "Episode 1",
                "Episode 2",
                "Episode 3",
                "Episode 33",
                "Episode 34",
            ],
            "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
            "episode_num": [1, 2, 3, 33, 34],
        }
    )


@fixture
def script():
    return Script(
        ref=EpisodeRef(
            episode_id="S01E02",
            episode_num=2,
            episode_title="Episode 2",
        ),
        script_lines=[
            ScriptLine(speaker="Jerry", dialogue="Hi, I'm Jerry."),
            ScriptLine(speaker="George", dialogue="Hi, I'm George."),
            ScriptLine(speaker="Kramer", dialogue="Hi, I'm Kramer."),
            ScriptLine(speaker="Elaine", dialogue="Hi, I'm Elaine."),
        ],
    )


class DummyScriptExtractor(ScriptExtractor):
    def extract_script(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        return pl.LazyFrame(
            {
                "episode_id": ["S01E02"] * 4,
                "episode_num": [2] * 4,
                "episode_title": ["Episode 2"] * 4,
                "speaker": ["Jerry", "George", "Kramer", "Elaine"],
                "dialogue": [
                    "Hi, I'm Jerry.",
                    "Hi, I'm George.",
                    "Hi, I'm Kramer.",
                    "Hi, I'm Elaine.",
                ],
            }
        )


class DummyCreditExtractor(CreditExtractor):
    def extract_credit(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        return pl.LazyFrame(
            {
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2"],
                "description": ["Seinfeld is literally a show about nothing."],
                "date": ["2025-01-01"],
                "writer": ["Larry David;Jerry Seinfeld"],
                "director": ["Jerry Seinfeld;Larry David"],
                "actors": [
                    "Jerry Seinfeld|Jerry;Jason Alexander|George;Julia Louis-Dreyfus|Elaine;Michael Richards|Kramer"
                ],
            }
        )


class DummyRatingExtractor(RatingExtractor):
    def extract_rating(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> pl.LazyFrame:
        return pl.LazyFrame(
            {
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2"],
                "rating": 10,
                "num_votes": 100,
                "link": "https://www.imdb.com/",
            }
        )


class DummyExporter(Exporter):
    def export(
        self, data: Union[List[Episode], List[Script], List[Rating], List[Credit]]
    ) -> None:
        return None


@fixture
def dummy_script_extractor() -> ScriptExtractor:
    return DummyScriptExtractor()


@fixture
def dummy_credit_extractor() -> CreditExtractor:
    return DummyCreditExtractor()


@fixture
def dummy_rating_extractor() -> RatingExtractor:
    return DummyRatingExtractor()


@fixture
def dummy_exporter() -> Exporter:
    return DummyExporter()


@fixture
def fake_omdb_response() -> dict:
    return {
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
