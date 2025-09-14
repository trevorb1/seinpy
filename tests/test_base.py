import pytest
import polars as pl
from polars.testing import assert_frame_equal

from seinpy.schema import Actor, Credit, Director, EpisodeRef, Rating, Writer


class TestScriptExtractor:
    @pytest.fixture
    def fake_df(self) -> pl.LazyFrame:
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

    def test_df_to_script(self, fake_df, dummy_script_extractor, script):
        extractor = dummy_script_extractor
        actual = extractor._df_to_script(fake_df)
        assert actual == script

    def test_extract_to_df(self, fake_df, dummy_script_extractor):
        extractor = dummy_script_extractor
        actual = extractor.extract(episode_id="S01E02", as_df=True)
        expected = fake_df.collect()
        assert_frame_equal(actual, expected)

    def test_is_one_episode_passes(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
            }
        )
        assert extractor._is_one_episode(df)

    def test_is_one_episode_fails(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02"],
                "episode_num": [1, 2],
                "episode_title": ["Episode 1", "Episode 2"],
            }
        )
        assert not extractor._is_one_episode(df)

    def test_is_one_episode_fails_missing_columns(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
            }
        )
        assert not extractor._is_one_episode(df)

    def test_coordinate_columns_passes(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "speaker": ["Jerry"],
                "dialogue": ["Hi, I'm Jerry."],
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
                "extra": ["extra"],
            }
        )
        expected = pl.LazyFrame(
            {
                "episode_num": [1],
                "episode_title": ["Episode 1"],
                "episode_id": ["S01E01"],
                "speaker": ["Jerry"],
                "dialogue": ["Hi, I'm Jerry."],
            }
        )
        actual = extractor._coordinate_columns(df)
        assert_frame_equal(actual, expected)

    def test_coordinate_columns_fails(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
            }
        )
        with pytest.raises(ValueError):
            extractor._coordinate_columns(df)

    def test_convert_episodeid_to_episodenum(self, dummy_script_extractor):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02", "S01E03"],
            }
        )
        actual = extractor._convert_episodeid_to_episodenum(df)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02", "S01E03"],
                "episode_num": pl.Series([1, 2, 3], dtype=pl.UInt32),
            }
        )
        assert_frame_equal(actual, expected)

    def test_convert_episodeid_to_episodenum_col_already_exists(
        self, dummy_script_extractor
    ):
        extractor = dummy_script_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02", "S01E03"],
                "episode_num": [5, 6, 7],
            }
        )
        actual = extractor._convert_episodeid_to_episodenum(df)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02", "S01E03"],
                "episode_num": pl.Series([1, 2, 3], dtype=pl.UInt32),
            }
        )
        assert_frame_equal(actual, expected)


class TestCreditExtractor:
    @pytest.fixture
    def fake_df(self) -> pl.LazyFrame:
        data = {
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
        return pl.LazyFrame(data)

    def test_df_to_credit_basic(self, dummy_credit_extractor, fake_df):
        extractor = dummy_credit_extractor
        actual = extractor._df_to_credits(fake_df)
        expected = Credit(
            ref=EpisodeRef(
                episode_id="S01E02", episode_num=2, episode_title="Episode 2"
            ),
            date="2025-01-01",
            writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
            directors=[Director(name="Jerry Seinfeld"), Director(name="Larry David")],
            description="Seinfeld is literally a show about nothing.",
            actors=[
                Actor(name="Jerry Seinfeld", role="Jerry"),
                Actor(name="Jason Alexander", role="George"),
                Actor(name="Julia Louis-Dreyfus", role="Elaine"),
                Actor(name="Michael Richards", role="Kramer"),
            ],
        )
        assert actual == expected

    def test_df_to_credit_no_actor_roles(self, dummy_credit_extractor, fake_df):
        extractor = dummy_credit_extractor
        fake_df = fake_df.with_columns(
            actors=pl.lit(
                "Jerry Seinfeld;Jason Alexander;Julia Louis-Dreyfus;Michael Richards"
            )
        )
        actual = extractor._df_to_credits(fake_df)
        expected = Credit(
            ref=EpisodeRef(
                episode_id="S01E02", episode_num=2, episode_title="Episode 2"
            ),
            date="2025-01-01",
            writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
            directors=[Director(name="Jerry Seinfeld"), Director(name="Larry David")],
            description="Seinfeld is literally a show about nothing.",
            actors=[
                Actor(name="Jerry Seinfeld"),
                Actor(name="Jason Alexander"),
                Actor(name="Julia Louis-Dreyfus"),
                Actor(name="Michael Richards"),
            ],
        )
        assert actual == expected

    def test_df_to_credit_multiple_episodes(self, dummy_credit_extractor):
        extractor = dummy_credit_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02"],
            }
        )
        with pytest.raises(ValueError):
            extractor._df_to_credits(df)

    def test_df_to_credit_missing_columns(self, dummy_credit_extractor):
        extractor = dummy_credit_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
            }
        )
        actual = extractor._df_to_credits(df)
        expected = Credit(
            ref=EpisodeRef(
                episode_id="S01E01", episode_num=1, episode_title="Episode 1"
            ),
            date="",
            writers=[],
            directors=[],
            description="",
            actors=[],
        )
        assert actual == expected

    def test_extract_to_df(self, dummy_credit_extractor, monkeypatch, fake_df):
        # Mock the extract_credits function
        monkeypatch.setattr(
            "seinpy.base.CreditExtractor.extract_credit",
            lambda *a, **k: fake_df,
        )

        extractor = dummy_credit_extractor
        actual = extractor.extract(episode_id="S01E02", as_df=True)
        expected = fake_df.collect()
        assert_frame_equal(actual, expected)

    def test_extract_to_credit(self, dummy_credit_extractor, monkeypatch, fake_df):
        # Mock the extract_credits function
        monkeypatch.setattr(
            "seinpy.base.CreditExtractor.extract_credit",
            lambda *a, **k: fake_df,
        )
        extractor = dummy_credit_extractor
        actual = extractor.extract(episode_id="S01E02", as_df=False)
        expected = Credit(
            ref=EpisodeRef(
                episode_id="S01E02",
                episode_num=2,
                episode_title="Episode 2",
            ),
            description="Seinfeld is literally a show about nothing.",
            date="2025-01-01",
            writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
            directors=[Director(name="Jerry Seinfeld"), Director(name="Larry David")],
            actors=[
                Actor(name="Jerry Seinfeld", role="Jerry"),
                Actor(name="Jason Alexander", role="George"),
                Actor(name="Julia Louis-Dreyfus", role="Elaine"),
                Actor(name="Michael Richards", role="Kramer"),
            ],
        )
        assert actual == expected


class TestRatingExtractor:
    def test_df_to_rating_basic(self, dummy_rating_extractor):
        extractor = dummy_rating_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
                "rating": [10],
                "num_votes": [100],
                "link": ["https://example.com"],
            }
        )
        actual = extractor._df_to_rating(df)
        expected = Rating(
            ref=EpisodeRef(
                episode_id="S01E01", episode_num=1, episode_title="Episode 1"
            ),
            rating=10,
            num_votes=100,
            link="https://example.com",
        )
        assert actual == expected

    def test_df_to_rating_missing_columns(self, dummy_rating_extractor):
        extractor = dummy_rating_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
            }
        )
        actual = extractor._df_to_rating(df)
        expected = Rating(
            ref=EpisodeRef(
                episode_id="S01E01", episode_num=1, episode_title="Episode 1"
            ),
            rating=None,
            num_votes=None,
            link=None,
        )
        assert actual == expected

    def test_df_to_rating_multiple_episodes(self, dummy_rating_extractor):
        extractor = dummy_rating_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01", "S01E02"],
            }
        )
        with pytest.raises(ValueError):
            extractor._df_to_rating(df)

    def test_df_to_rating_wrong_dtype(self, dummy_rating_extractor):
        extractor = dummy_rating_extractor
        df = pl.LazyFrame(
            {
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "episode_title": ["Episode 1"],
                "rating": ["10"],
                "num_votes": ["100"],
                "link": ["https://example.com"],
            }
        )
        actual = extractor._df_to_rating(df)
        expected = Rating(
            ref=EpisodeRef(
                episode_id="S01E01", episode_num=1, episode_title="Episode 1"
            ),
            rating=10.0,
            num_votes=100,
            link="https://example.com",
        )
        assert actual == expected
