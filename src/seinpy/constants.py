"""Constants and enumerations used across seinpy."""

from enum import StrEnum
from pathlib import Path

import polars as pl


class ScriptSource(StrEnum):
    """Available script extractor sources."""
    KAGGLE = "kaggle"
    IMDB = "imdb"
    SEINFELDSCRIPTS = "seinfeldscripts"
    SEINOLOGY = "seinology"


class CreditSource(StrEnum):
    """Available credit extractor sources."""
    OMDB = "omdb"
    ROTTENTOMATOES = "rottentomatoes"


class RatingSource(StrEnum):
    """Available rating extractor sources."""
    OMDB = "omdb"
    ROTTENTOMATOES = "rottentomatoes"


class ExporterType(StrEnum):
    """Available exporter types."""
    DATABASE = "database"
    CSV = "csv"
    JSON = "json"


SCRIPT_EXTRACTORS = [s.value for s in ScriptSource]
CREDIT_EXTRACTORS = [c.value for c in CreditSource]
RATING_EXTRACTORS = [r.value for r in RatingSource]
EXPORTERS = [e.value for e in ExporterType]

TWO_PART_EPISODES = [
    {"episode_id": "S03E17", "episode_num": 34, "episode_title": "The Boyfriend"},
    {"episode_id": "S04E23", "episode_num": 62, "episode_title": "The Pilot"},
    {"episode_id": "S05E18", "episode_num": 80, "episode_title": "The Raincoats"},
    {
        "episode_id": "S06E14",
        "episode_num": 97,
        "episode_title": "The Highlights of a Hundred",
    },
    {"episode_id": "S07E14", "episode_num": 120, "episode_title": "The Cadillac"},
    {"episode_id": "S07E20", "episode_num": 126, "episode_title": "The Bottle Deposit"},
    {"episode_id": "S09E21", "episode_num": 171, "episode_title": "The Chronicle"},
    {"episode_id": "S09E22", "episode_num": 172, "episode_title": "The Finale"},
]

METADATA = pl.scan_csv(Path(Path(__file__).parent, "data", "data.csv"))

OMDB_API = "http://www.omdbapi.com/"
