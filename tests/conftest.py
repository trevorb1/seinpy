from pytest import fixture
import polars as pl
from seinpy.base import ScriptExtractor, CreditExtractor, RatingExtractor
from seinpy.schema import Actor, Script, Credit, Rating, EpisodeRef, ScriptLine


@fixture
def metadata() -> pl.LazyFrame:
    """Metadata for the Seinfeld scripts."""
    return pl.LazyFrame(
        {
            "episode_title": [
                "Good News, Bad News",
                "The Stakeout",
                "The Robbery",
                "The Fix-Up",
                "The Boyfriend",
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
                "Good News, Bad News",
                "The Stakeout",
                "The Robbery",
                "The Fix-Up",
                "The Boyfriend",
            ],
            "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
            "episode_num": [1, 2, 3, 33, 34],
        }
    )


class DummyScriptExtractor(ScriptExtractor):
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Script | pl.DataFrame:
        if as_df:
            return pl.DataFrame(
                {
                    "episode_id": ["S01E01"] * 4,
                    "episode_num": [1] * 4,
                    "episode_title": ["Good News, Bad News"] * 4,
                    "speaker": ["Jerry", "George", "Kramer", "Elaine"],
                    "dialogue": [
                        "Jerry: Hi, I'm Jerry.",
                        "George: Hi, I'm George.",
                        "Kramer: Hi, I'm Kramer.",
                        "Elaine: Hi, I'm Elaine.",
                    ],
                }
            )
        return Script(
            ref=EpisodeRef(
                episode_id="S01E01",
                episode_num=1,
                episode_title="Good News, Bad News",
            ),
            script_lines=[
                ScriptLine(speaker="Jerry", dialogue="Jerry: Hi, I'm Jerry."),
                ScriptLine(speaker="George", dialogue="George: Hi, I'm George."),
                ScriptLine(speaker="Kramer", dialogue="Kramer: Hi, I'm Kramer."),
                ScriptLine(speaker="Elaine", dialogue="Elaine: Hi, I'm Elaine."),
            ],
        )


class DummyCreditExtractor(CreditExtractor):
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Credit | pl.DataFrame:
        if as_df:
            return pl.DataFrame(
                {
                    "episode_id": ["S01E01"],
                    "episode_num": [1],
                    "episode_title": ["Good News, Bad News"],
                    "description": ["This is the pilot episode of Seinfeld."],
                    "date": ["1989-07-05"],
                    "writer": ["Jerry Seinfeld;Larry David"],
                    "director": ["Jerry Seinfeld;Larry David"],
                    "actors": [
                        "Jerry Seinfeld|Jerry;Jason Alexander|George;Julia Louis-Dreyfus|Elaine;Michael Richards|Kramer"
                    ],
                }
            )
        return Credit(
            ref=EpisodeRef(
                episode_id="S01E01",
                episode_num=1,
                episode_title="Good News, Bad News",
            ),
            description="This is the pilot episode of Seinfeld.",
            date="1989-07-05",
            writer=["Jerry Seinfeld", "Larry David"],
            director=["Jerry Seinfeld", "Larry David"],
            actors=[
                Actor(name="Jerry Seinfeld", role="Jerry"),
                Actor(name="Jason Alexander", role="George"),
                Actor(name="Michael Richards", role="Kramer"),
                Actor(name="Julia Louis-Dreyfus", role="Elaine"),
            ],
        )


class DummyRatingExtractor(RatingExtractor):
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
        as_df: bool = False,
    ) -> Rating | pl.DataFrame:
        if as_df:
            return pl.DataFrame(
                {
                    "episode_id": ["S01E01"],
                    "episode_num": [1],
                    "episode_title": ["Good News, Bad News"],
                    "rating": 10,
                    "num_votes": 100,
                    "link": "https://www.imdb.com/",
                }
            )
        return Rating(
            ref=EpisodeRef(
                episode_id="S01E01",
                episode_num=1,
                episode_title="Good News, Bad News",
            ),
            rating=10,
            num_votes=100,
            link="https://www.imdb.com/",
        )


@fixture
def dummy_script_extractor() -> ScriptExtractor:
    return DummyScriptExtractor()


@fixture
def dummy_credit_extractor() -> CreditExtractor:
    return DummyCreditExtractor()


@fixture
def dummy_rating_extractor() -> RatingExtractor:
    return DummyRatingExtractor()
