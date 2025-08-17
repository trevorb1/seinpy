import pytest
import polars as pl
from polars.testing import assert_frame_equal
from seinpy.utils import (
    get_omdb_api_key,
    get_episode_filter_priority,
    filter_metadata,
    get_episode_ids_from_seasons,
    shift_episode_ids,
    shift_episode_nums,
)


class TestGetOmdbApiKey:
    def test_get_omdb_api_key_from_user(self):
        key = "key"
        assert get_omdb_api_key(key) == "key"

    def test_get_omdb_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("OMDB", "key")
        assert get_omdb_api_key() == "key"

    def test_get_omdb_api_key_no_key(self):
        with pytest.raises(ValueError):
            get_omdb_api_key()


@pytest.mark.parametrize(
    "episode_id, episode_num, episode_title, expected",
    [
        ("S01E01", None, None, "episode_id"),
        (None, 1, None, "episode_num"),
        (None, None, "The Stakeout", "episode_title"),
        (None, None, None, ""),
        ("S01E01", 1, "The Stakeout", "episode_id"),
        (None, 1, "The Stakeout", "episode_num"),
    ],
)
def test_get_episode_filter_priority(episode_id, episode_num, episode_title, expected):
    assert (
        get_episode_filter_priority(episode_id, episode_num, episode_title) == expected
    )


class TestFilterMetadata:
    def test_filter_metadata_episode_id(self, metadata):
        actual = filter_metadata(episode_id="S01E01", metadata=metadata)
        expected = pl.LazyFrame(
            {
                "episode_title": ["Good News, Bad News"],
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "imdb": ["tt0098286"],
            }
        )
        assert_frame_equal(actual, expected)

    def test_filter_metadata_episode_num(self, metadata):
        actual = filter_metadata(episode_num=1, metadata=metadata)
        expected = pl.LazyFrame(
            {
                "episode_title": ["Good News, Bad News"],
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "imdb": ["tt0098286"],
            }
        )
        assert_frame_equal(actual, expected)

    def test_filter_metadata_episode_title(self, metadata):
        actual = filter_metadata(episode_title="The Stakeout", metadata=metadata)
        expected = pl.LazyFrame(
            {
                "episode_title": ["The Stakeout"],
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "imdb": ["tt0697784"],
            }
        )
        assert_frame_equal(actual, expected)

    def test_filter_metadata_no_inputs(self):
        with pytest.raises(ValueError):
            filter_metadata()


class TestGetEpisodeIdsFromSeasons:
    def test_get_episode_ids_from_one_season(self, metadata):
        actual = get_episode_ids_from_seasons(seasons=1, metadata=metadata)
        expected = ["S01E01", "S01E02", "S01E03"]
        assert actual == expected

    def test_get_episode_ids_from_one_season_as_list(self, metadata):
        actual = get_episode_ids_from_seasons(seasons=[1], metadata=metadata)
        expected = ["S01E01", "S01E02", "S01E03"]
        assert actual == expected

    def test_get_episode_ids_from_multiple_seasons(self, metadata):
        actual = get_episode_ids_from_seasons(seasons=[1, 3], metadata=metadata)
        expected = ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"]
        assert actual == expected


class TestShiftEpisodeIds:
    def test_shift_episode_ids(self, episode_reference):
        actual = shift_episode_ids(df=episode_reference, from_episode_id="S01E02")
        expected = pl.LazyFrame(
            {
                "episode_title": [
                    "Good News, Bad News",
                    "The Stakeout",
                    "The Robbery",
                    "The Fix-Up",
                    "The Boyfriend",
                ],
                "episode_id": ["S01E01", "S01E02", "S01E02", "S03E16", "S03E17"],
                "episode_num": [1, 2, 3, 33, 34],
            }
        )
        assert_frame_equal(actual, expected)

    def test_shift_episode_ids_no_id_found(self, episode_reference):
        actual = shift_episode_ids(df=episode_reference, from_episode_id="S02E01")
        expected = episode_reference
        assert_frame_equal(actual, expected)


class TestShiftEpisodeNums:
    def test_shift_episode_nums(self, episode_reference):
        actual = shift_episode_nums(df=episode_reference, from_episode_num=2)
        expected = pl.LazyFrame(
            {
                "episode_title": [
                    "Good News, Bad News",
                    "The Stakeout",
                    "The Robbery",
                    "The Fix-Up",
                    "The Boyfriend",
                ],
                "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
                "episode_num": [1, 2, 2, 32, 33],
            }
        )
        assert_frame_equal(actual, expected)

    def test_shift_episode_nums_no_num_found(self, episode_reference):
        actual = shift_episode_nums(df=episode_reference, from_episode_num=10)
        expected = pl.LazyFrame(
            {
                "episode_title": [
                    "Good News, Bad News",
                    "The Stakeout",
                    "The Robbery",
                    "The Fix-Up",
                    "The Boyfriend",
                ],
                "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
                "episode_num": [1, 2, 3, 32, 33],
            }
        )
        assert_frame_equal(actual, expected)
