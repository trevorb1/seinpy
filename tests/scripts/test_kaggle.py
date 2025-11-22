import pytest

from seinpy.scripts.kaggle import KaggleScriptExtractor

import polars as pl
from polars.testing import assert_frame_equal

from pathlib import Path

TEST_DIR = Path(__file__).parent.parent.resolve()  # tests/


@pytest.fixture
def kaggle_extractor(monkeypatch):
    fake_zip_folder = Path(TEST_DIR, "scripts", "fixtures", "kaggle")
    monkeypatch.setattr(
        "seinpy.scripts.kaggle.KaggleScriptExtractor._download_data",
        lambda *a, **k: fake_zip_folder,
    )

    return KaggleScriptExtractor()


class TestKaggleScriptExtractor:
    def test_download_data_returns_mocked_path(self, kaggle_extractor):
        assert kaggle_extractor.zip_folder == Path(
            TEST_DIR, "scripts", "fixtures", "kaggle"
        )

    def test_download_data(self, monkeypatch):
        """Test that _download_data calls kagglehub.dataset_download and returns the path.

        Can not use the kaggle_extractor fixture because it calls _download_data itself.
        """
        expected_path = Path("/fake/kaggle/path")

        def mock_dataset_download(dataset_name):
            assert dataset_name == "thec03u5/seinfeld-chronicles"
            return str(expected_path)

        monkeypatch.setattr(
            "seinpy.scripts.kaggle.kagglehub.dataset_download", mock_dataset_download
        )
        monkeypatch.setattr(
            "seinpy.scripts.kaggle.KaggleScriptExtractor._get_raw_data",
            lambda self: pl.DataFrame(),
        )

        extractor = KaggleScriptExtractor()
        result = extractor._download_data()

        assert result == str(expected_path)

    def test_read_script(self, kaggle_extractor):
        script = kaggle_extractor._read_script()
        assert isinstance(script, pl.LazyFrame)
        df = script.collect()

        assert len(df) > 0

        expected_columns = ["speaker", "dialogue", "episode_num", "episode_id"]
        assert all(col in df.columns for col in expected_columns)

        unique_episode_ids = df["episode_id"].unique().sort().to_list()
        assert unique_episode_ids == ["S01E01", "S01E02", "S01E03"]

        unique_episode_nums = df["episode_num"].unique().sort().to_list()
        assert unique_episode_nums == [1, 2, 3]

    def test_read_episode_info(self, kaggle_extractor):
        episode_info = kaggle_extractor._read_episode_info()
        assert isinstance(episode_info, pl.LazyFrame)
        df = episode_info.collect()

        assert len(df) > 0

        expected_columns = ["episode_num", "episode_id", "episode_title"]
        assert all(col in df.columns for col in expected_columns)

        unique_episode_ids = df["episode_id"].unique().sort().to_list()
        assert unique_episode_ids == ["S01E01", "S01E02", "S01E03", "S04E23", "S04E24"]

        unique_episode_nums = df["episode_num"].unique().sort().to_list()
        assert unique_episode_nums == [1, 2, 3, 23, 24]

        unique_episode_titles = df["episode_title"].to_list()
        assert unique_episode_titles == [
            "Good News, Bad News",
            "The Stakeout",
            "The Robbery",
            "Male Unbonding",
            "The Pilot (1)",
            "The Pilot (2)",
        ]

    def test_correct_pilot_episode_id(self, kaggle_extractor):
        original = kaggle_extractor._read_episode_info()
        corrected = kaggle_extractor._correct_pilot_episode_id(original)
        assert isinstance(corrected, pl.LazyFrame)
        corrected = corrected.collect()

        episode_ids = corrected["episode_id"].unique().sort().to_list()
        assert episode_ids == [
            "S01E01",
            "S01E02",
            "S01E03",
            "S01E04",
            "S04E23",
            "S04E24",
        ]

        original = original.drop("episode_id")
        corrected = corrected.drop("episode_id")

        original = original.collect()
        assert_frame_equal(original, corrected)

    def test_adjust_episode_num_assertion_error(self, kaggle_extractor):
        original = kaggle_extractor._read_episode_info()
        original = original.collect()

        with pytest.raises(AssertionError):
            kaggle_extractor._adjust_episode_num(original)

    def test_adjust_episode_num(self, kaggle_extractor):
        original = kaggle_extractor._read_episode_info()
        adjusted = kaggle_extractor._correct_pilot_episode_id(original)
        corrected = kaggle_extractor._adjust_episode_num(adjusted)

        assert isinstance(corrected, pl.LazyFrame)

        corrected = corrected.collect()
        episode_nums = corrected["episode_num"].unique().sort().to_list()
        assert episode_nums == [1, 2, 3, 4, 24, 25]

        adjusted = adjusted.drop("episode_num")
        corrected = corrected.drop("episode_num")

        adjusted = adjusted.collect()
        assert_frame_equal(adjusted, corrected)

    def test_correct_2_part_episodes(self, kaggle_extractor):
        original = kaggle_extractor._read_episode_info()
        corrected = kaggle_extractor._correct_2_part_episodes(original)
        assert isinstance(corrected, pl.LazyFrame)

        corrected = corrected.collect()
        episode_titles = corrected["episode_title"].to_list()

        assert episode_titles == [
            "Good News, Bad News",
            "The Stakeout",
            "The Robbery",
            "Male Unbonding",
            "The Pilot",
            "The Pilot",
        ]

    def test_extract_script_by_episode_id(self, kaggle_extractor):
        script = kaggle_extractor.extract_script(episode_id="S01E01")
        assert isinstance(script, pl.LazyFrame)
        df = script.collect()

        assert len(df) > 0

        expected_columns = ["speaker", "dialogue", "episode_num", "episode_id"]
        assert all(col in df.columns for col in expected_columns)

        unique_episode_ids = df["episode_id"].unique().sort().to_list()
        assert unique_episode_ids == ["S01E01"]

    def test_extract_script_by_episode_num(self, kaggle_extractor):
        script = kaggle_extractor.extract_script(episode_num=1)
        assert isinstance(script, pl.LazyFrame)
        df = script.collect()

        assert len(df) > 0

        expected_columns = ["speaker", "dialogue", "episode_num", "episode_id"]
        assert all(col in df.columns for col in expected_columns)

        unique_episode_nums = df["episode_num"].unique().sort().to_list()
        assert unique_episode_nums == [1]

    def test_extract_script_by_episode_title(self, kaggle_extractor):
        script = kaggle_extractor.extract_script(episode_title="Good News, Bad News")
        assert isinstance(script, pl.LazyFrame)
        df = script.collect()

        assert len(df) > 0

        expected_columns = ["speaker", "dialogue", "episode_num", "episode_id"]
        assert all(col in df.columns for col in expected_columns)

        unique_episode_titles = df["episode_title"].unique().to_list()
        assert unique_episode_titles == ["Good News, Bad News"]

    def test_extract_script_error_multiple_episodes_found(self, kaggle_extractor):
        with pytest.raises(ValueError):
            kaggle_extractor.extract_script(episode_title="The Pilot")

    def test_extract_script_error(self, kaggle_extractor):
        with pytest.raises(ValueError):
            kaggle_extractor.extract_script()
