from pytest import fixture
import polars as pl


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