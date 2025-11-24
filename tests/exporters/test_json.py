import json
import pytest
from seinpy.exporters.json import JsonExporter


@pytest.fixture
def expected_json():
    return {
        "ref": {
            "episode_id": "S01E02",
            "episode_num": 2,
            "episode_title": "Episode 2.",
        },
        "script": {
            "script_lines": [
                {
                    "speaker": "Jerry",
                    "dialogue": "Hi, I'm Jerry.",
                },
                {
                    "speaker": "George",
                    "dialogue": "Hi, I'm George.",
                },
                {
                    "speaker": "Kramer",
                    "dialogue": "Hi, I'm Kramer.",
                },
                {
                    "speaker": "Elaine",
                    "dialogue": "Hi, I'm Elaine.",
                },
            ]
        },
        "credit": {
            "description": "Seinfeld is literally a show about nothing.",
            "date": "2025-01-01",
            "writers": [
                {
                    "name": "Larry David",
                },
                {
                    "name": "Jerry Seinfeld",
                },
            ],
            "directors": [
                {
                    "name": "Jerry Seinfeld",
                },
                {
                    "name": "Larry David",
                },
            ],
            "actors": [
                {
                    "name": "Jerry Seinfeld",
                    "role": "Jerry",
                },
                {
                    "name": "Jason Alexander",
                    "role": "George",
                },
                {
                    "name": "Julia Louis-Dreyfus",
                    "role": "Elaine",
                },
                {
                    "name": "Michael Richards",
                    "role": "Kramer",
                },
            ],
        },
        "rating": {
            "rating": 10.0,
            "num_votes": 100,
            "link": "https://example.com",
        },
    }


class TestJsonExporter:
    def test_convert_to_json(self, fake_episode, expected_json):
        actual = JsonExporter().convert_to_json(fake_episode)
        expected = [expected_json]
        assert actual == expected

    def test_multiple_episodes_convert_to_json(self, fake_episode, expected_json):
        actual = JsonExporter().convert_to_json([fake_episode, fake_episode])
        expected = []
        expected.append(expected_json)
        expected.append(expected_json)
        assert actual == expected

    def test_export(self, fake_episode, expected_json, tmp_path):
        save_path = tmp_path / "test_export.json"
        JsonExporter().export([fake_episode], str(save_path))

        assert save_path.exists()
        with open(save_path, "r") as f:
            actual = json.load(f)

        expected = [expected_json]
        assert actual == expected
