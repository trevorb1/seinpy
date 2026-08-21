from pathlib import Path

import polars as pl

SCRIPT_EXTRACTORS = ["kaggle", "imdb", "seinfeldscripts", "seinology"]
CREDIT_EXTRACTORS = ["omdb", "rottentomatoes"]
RATING_EXTRACTORS = ["omdb"]
EXPORTERS = ["database", "csv", "json"]

TWO_PART_EPISODES = [
    {"episode_id": "S03E17", "episode_num": 34, "episode_title": "The Boyfriend"},
    {"episode_id": "S04E23", "episode_num": 62, "episode_title": "The Pilot"},
    {"episode_id": "S05E18", "episode_num": 80, "episode_title": "The Raincoats"},
    {
        "episode_id": "S06E14",
        "episode_num": 97,
        "episode_title": "The Highlights of a Hundred",
    },
    {"episode_id": "S07E14", "episode_num": 123, "episode_title": "The Cadillac"},
    {"episode_id": "S07E20", "episode_num": 126, "episode_title": "The Bottle Deposit"},
    {"episode_id": "S09E21", "episode_num": 171, "episode_title": "The Chronicle"},
    {"episode_id": "S09E22", "episode_num": 172, "episode_title": "The Finale"},
]

METADATA = pl.scan_csv(Path(Path(__file__).parent, "data", "data.csv"))

OMDB_API = "http://www.omdbapi.com/"