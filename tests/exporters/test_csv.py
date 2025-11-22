import polars as pl
from polars.testing import assert_frame_equal
import pytest

from seinpy.exporters.csv import CsvExporter

@pytest.fixture
def expected_episode_df():
    return pl.LazyFrame(
            {
                "episode_id": ["S01E02"] * 4,
                "episode_num": [2] * 4,
                "episode_title": ["Episode 2."] * 4,
                "speaker": [
                    "Jerry",
                    "George",
                    "Kramer",
                    "Elaine",
                ],
                "dialogue": [
                    "Hi, I'm Jerry.",
                    "Hi, I'm George.",
                    "Hi, I'm Kramer.",
                    "Hi, I'm Elaine.",
                ],
                "description": ["Seinfeld is literally a show about nothing."] * 4,
                "date": ["2025-01-01"] * 4,
                "writers": ["Larry David;Jerry Seinfeld"] * 4,
                "directors": ["Jerry Seinfeld;Larry David"] * 4,
                "actors": [
                    "Jerry Seinfeld|Jerry;Jason Alexander|George;Julia Louis-Dreyfus|Elaine;Michael Richards|Kramer"
                ]
                * 4,
                "rating": [10.0] * 4,
                "num_votes": [100] * 4,
                "link": ["https://example.com"] * 4,
            }
        )

class TestCsvExporter:
    def test_episode_ref_to_dataframe(self, fake_episode_ref):
        actual = CsvExporter._episode_ref_to_dataframe(fake_episode_ref)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2."],
            }
        )
        assert_frame_equal(actual, expected)

    def test_script_to_dataframe(self, fake_script):
        actual = CsvExporter._script_to_dataframe(fake_script)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E02"] * 4,
                "episode_num": [2] * 4,
                "episode_title": ["Episode 2."] * 4,
                "speaker": ["Jerry", "George", "Kramer", "Elaine"],
                "dialogue": [
                    "Hi, I'm Jerry.",
                    "Hi, I'm George.",
                    "Hi, I'm Kramer.",
                    "Hi, I'm Elaine.",
                ],
            }
        )
        assert_frame_equal(actual, expected)

    def test_credit_to_dataframe(self, fake_credit):
        actual = CsvExporter._credit_to_dataframe(fake_credit)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2."],
                "description": ["Seinfeld is literally a show about nothing."],
                "date": ["2025-01-01"],
                "writers": ["Larry David;Jerry Seinfeld"],
                "directors": ["Jerry Seinfeld;Larry David"],
                "actors": [
                    "Jerry Seinfeld|Jerry;Jason Alexander|George;Julia Louis-Dreyfus|Elaine;Michael Richards|Kramer"
                ],
            }
        )
        assert_frame_equal(actual, expected)

    def test_rating_to_dataframe(self, fake_rating):
        actual = CsvExporter._rating_to_dataframe(fake_rating)
        expected = pl.LazyFrame(
            {
                "episode_id": ["S01E02"],
                "episode_num": [2],
                "episode_title": ["Episode 2."],
                "rating": [10.0],
                "num_votes": [100],
                "link": ["https://example.com"],
            }
        )
        assert_frame_equal(actual, expected)

    def test_convert_to_dataframe_wrong_dtype(self):
        exporter = CsvExporter()
        with pytest.raises(ValueError):
            exporter.convert_to_dataframe("not a list of episodes")
        with pytest.raises(ValueError):
            exporter.convert_to_dataframe(["wrong list type"])

    def test_convert_to_dataframe(self, fake_episode, expected_episode_df):
        actual = CsvExporter().convert_to_dataframe([fake_episode])
        expected = expected_episode_df
        assert_frame_equal(actual, expected)

    def test_export(self, fake_episode, expected_episode_df, tmp_path):
        """Test that export creates a CSV file with the correct data."""
        save_path = tmp_path / "test_export.csv"
        exporter = CsvExporter()
        exporter.export([fake_episode], str(save_path))

        assert save_path.exists()

        actual = pl.read_csv(save_path)
        expected = expected_episode_df.collect()
        assert_frame_equal(actual, expected)
