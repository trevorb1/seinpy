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

    # def test_join_script_and_info(self, kaggle_extractor):
    #     script = kaggle_extractor._read_script()
    #     episode_info = kaggle_extractor._read_episode_info()
    #     joined = kaggle_extractor._join_script_and_info(episode_info, script)
    #     assert isinstance(joined, pl.LazyFrame)
    #     actual = joined.collect()
    #     assert len(actual) > 0
    #     assert all(
    #         col in actual.columns
    #         for col in [
    #             "episode_num",
    #             "episode_title",
    #             "episode_id",
    #             "speaker",
    #             "dialogue",
    #         ]
    #     )
    #     expected = (
    #         pl.LazyFrame(
    #             {
    #                 "episode_num": [1] * 6 + [2] * 3 + [3] * 3,
    #                 "episode_title": ["Good News, Bad News"] * 6
    #                 + ["The Stakeout"] * 3
    #                 + ["The Robbery"] * 3,
    #                 "episode_id": ["S01E01"] * 6 + ["S01E02"] * 3 + ["S01E03"] * 3,
    #                 "speaker": [
    #                     "JERRY",
    #                     "JERRY",
    #                     "GEORGE",
    #                     "JERRY",
    #                     "GEORGE",
    #                     "JERRY",
    #                     "GEORGE",
    #                     "JERRY",
    #                     "CLAIRE",
    #                     "GEORGE",
    #                     "JERRY",
    #                     "CLAIRE",
    #                 ],
    #                 "dialogue": [
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm George. ",
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm George. ",
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm George. ",
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm Claire. ",
    #                     "Hi, I'm George. ",
    #                     "Hi, I'm Jerry. ",
    #                     "Hi, I'm Claire. ",
    #                 ],
    #             }
    #         )
    #         .with_columns([pl.col("episode_num").cast(pl.Int8)])
    #         .collect()
    #     )
    #     print(actual)
    #     print(expected)
    #     assert_frame_equal(actual, expected)

    # def test_extract_script_by_episode_id(self, kaggle_extractor):
    #     script = kaggle_extractor.extract_script(episode_id="S01E01")
    #     assert isinstance(script, pl.LazyFrame)
    #     df = script.collect()
    #     assert len(df) > 0
    #     assert all(
    #         col in df.columns
    #         for col in [
    #             "episode_id",
    #             "episode_num",
    #             "episode_title",
    #             "speaker",
    #             "dialogue",
    #         ]
    #     )
    #     assert all(df["episode_id"] == "S01E01")

    # def test_extract_script_by_episode_num(self, kaggle_extractor):
    #     script = kaggle_extractor.extract_script(episode_num=1)
    #     df = script.collect()
    #     assert len(df) > 0
    #     assert all(df["episode_num"] == 1)

    # def test_extract_script_by_episode_title(self, kaggle_extractor):
    #     script = kaggle_extractor.extract_script(
    #         episode_title="The Seinfeld Chronicles."
    #     )
    #     df = script.collect()
    #     assert len(df) > 0
    #     assert all(df["episode_title"] == "The Seinfeld Chronicles")

    # def test_extract_script_no_params(self, kaggle_extractor):
    #     with pytest.raises(
    #         ValueError, match="No episode_id, episode_num, or episode_title provided"
    #     ):
    #         kaggle_extractor.extract_script()

    # def test_extract_script_multiple_episodes(self, kaggle_extractor):
    #     with pytest.raises(ValueError):
    #         kaggle_extractor.extract_script(
    #             episode_title="The"
    #         )  # Should match multiple episodes

    # def test_raw_data_structure(self, kaggle_extractor):
    #     data = kaggle_extractor.data
    #     assert isinstance(data, pl.LazyFrame)
    #     df = data.collect()
    #     assert all(
    #         col in df.columns
    #         for col in [
    #             "episode_id",
    #             "episode_num",
    #             "episode_title",
    #             "speaker",
    #             "dialogue",
    #         ]
    #     )

    # def test_two_part_episodes_correction(self, kaggle_extractor):
    #     data = kaggle_extractor.data.collect()
    #     # Check that no episode titles end with (1) or (2)
    #     assert not data["episode_title"].str.contains(r" \(\d+\)$").any()
