import polars as pl
import pytest
from polars.testing import assert_frame_equal

from seinpy.utils import (
    filter_metadata,
    get_episode_filter_priority,
    get_episode_id_num_title,
    get_episode_ids_from_seasons,
    get_omdb_api_key,
    is_valid_extractors,
    shift_episode_ids,
    shift_episode_nums,
)


class TestGetOmdbApiKey:
    def test_get_omdb_api_key_from_user(self):
        key = "key"
        assert get_omdb_api_key(key) == "key"

    def test_get_omdb_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("OMDB_API_KEY", "key")
        assert get_omdb_api_key() == "key"

    def test_get_omdb_api_key_no_key(self, monkeypatch):
        monkeypatch.delenv("OMDB_API_KEY", raising=False)
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
                "episode_title": ["Episode 1"],
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
                "episode_title": ["Episode 1"],
                "episode_id": ["S01E01"],
                "episode_num": [1],
                "imdb": ["tt0098286"],
            }
        )
        assert_frame_equal(actual, expected)

    def test_filter_metadata_episode_title(self, metadata):
        actual = filter_metadata(episode_title="Episode 2", metadata=metadata)
        expected = pl.LazyFrame(
            {
                "episode_title": ["Episode 2"],
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
                    "Episode 1",
                    "Episode 2",
                    "Episode 3",
                    "Episode 33",
                    "Episode 34",
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
                    "Episode 1",
                    "Episode 2",
                    "Episode 3",
                    "Episode 33",
                    "Episode 34",
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
                    "Episode 1",
                    "Episode 2",
                    "Episode 3",
                    "Episode 33",
                    "Episode 34",
                ],
                "episode_id": ["S01E01", "S01E02", "S01E03", "S03E16", "S03E17"],
                "episode_num": [1, 2, 3, 32, 33],
            }
        )
        assert_frame_equal(actual, expected)


class TestGetEpisodeIdNumTitle:
    def test_get_episode_id_num_title(self, metadata):
        actual = get_episode_id_num_title(df=metadata, episode_id="S01E01")
        expected = ("S01E01", 1, "Episode 1")
        assert actual == expected

    def test_get_episode_id_num_title_no_arguments(self, metadata):
        with pytest.raises(ValueError):
            get_episode_id_num_title(df=metadata)

    def test_get_episode_id_num_title_no_episode_num(self, metadata):
        actual = get_episode_id_num_title(df=metadata, episode_title="Episode 1")
        expected = ("S01E01", 1, "Episode 1")
        assert actual == expected

    def test_get_episode_id_num_title_no_episode_title(self, metadata):
        actual = get_episode_id_num_title(
            df=metadata, episode_id="S01E01", episode_num=3
        )
        expected = ("S01E01", 1, "Episode 1")
        assert actual == expected

    def test_get_episode_id_num_title_episode_id_num_title(self, metadata):
        actual = get_episode_id_num_title(
            df=metadata, episode_id="S01E01", episode_num=3, episode_title="Title"
        )
        expected = ("S01E01", 1, "Episode 1")
        assert actual == expected

    def test_get_episode_id_num_title_no_episode_id(self, metadata):
        actual = get_episode_id_num_title(
            df=metadata, episode_num=3, episode_title="Title"
        )
        expected = ("S01E03", 3, "Episode 3")
        assert actual == expected

    def test_get_episode_id_num_title_invalid_arg(self, metadata):
        with pytest.raises(ValueError):
            get_episode_id_num_title(df=metadata, episode_id="invalid")

    def test_get_episode_id_num_title_invalid_schema(self):
        wrong_metadata = pl.LazyFrame(
            {
                "wrong_header": ["Episode 1"],
                "another_wrong_header": ["S01E01"],
                "yet_another_wrong_header": [1],
            }
        )
        with pytest.raises(ValueError):
            get_episode_id_num_title(df=wrong_metadata, episode_id="S01E01")


class TestIsValidExtractors:
    def test_is_valid_extractors_empty_dict(self):
        assert is_valid_extractors({}) is True

    def test_is_valid_extractors_all_none(self):
        source = {"script": None, "credit": None, "rating": None}
        assert is_valid_extractors(source) is True

    def test_is_valid_extractors_valid_script(self):
        source = {"script": "kaggle"}
        assert is_valid_extractors(source) is True

    def test_is_valid_extractors_valid_credit(self):
        source = {"credit": "omdb"}
        assert is_valid_extractors(source) is True

    def test_is_valid_extractors_valid_rating(self):
        source = {"rating": "omdb"}
        assert is_valid_extractors(source) is True

    def test_is_valid_extractors_all_valid_extractors(self):
        source = {"script": "imdb", "credit": "rottentomatoes", "rating": "omdb"}
        assert is_valid_extractors(source) is True

    def test_is_valid_extractors_all_script_extractors(self):
        for extractor in ["kaggle", "imdb", "seinfeldscripts", "seinology"]:
            source = {"script": extractor}
            assert is_valid_extractors(source) is True

    def test_is_valid_extractors_all_credit_extractors(self):
        for extractor in ["omdb", "rottentomatoes"]:
            source = {"credit": extractor}
            assert is_valid_extractors(source) is True

    def test_is_valid_extractors_all_rating_extractors(self):
        for extractor in ["omdb"]:
            source = {"rating": extractor}
            assert is_valid_extractors(source) is True

    def test_is_valid_extractors_invalid_script_extractor(self):
        source = {"script": "invalid_script"}
        assert is_valid_extractors(source) is False

    def test_is_valid_extractors_invalid_credit_extractor(self):
        source = {"credit": "invalid_credit"}
        assert is_valid_extractors(source) is False

    def test_is_valid_extractors_invalid_rating_extractor(self):
        source = {"rating": "invalid_rating"}
        assert is_valid_extractors(source) is False

    def test_is_valid_extractors_invalid_key(self):
        source = {"invalid_key": "some_value"}
        assert is_valid_extractors(source) is False

    def test_is_valid_extractors_invalid_key_with_valid_extractors(self):
        source = {"script": "kaggle", "invalid_key": "some_value"}
        assert is_valid_extractors(source) is False

    def test_is_valid_extractors_not_a_dict(self):
        with pytest.raises(ValueError):
            is_valid_extractors("kaggle")

    def test_is_valid_extractors_source_dataclass(self):
        from seinpy.base import Source
        source = Source(script="kaggle", credit="omdb", rating="omdb")
        assert is_valid_extractors(source) is True

        source = Source(script="invalid_script")
        assert is_valid_extractors(source) is False
