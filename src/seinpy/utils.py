"""Utility functions for extractors."""

import logging
import os
from typing import Any

import polars as pl

from seinpy.base import Source
from seinpy.constants import (
    CREDIT_EXTRACTORS,
    METADATA,
    RATING_EXTRACTORS,
    SCRIPT_EXTRACTORS,
)

logger = logging.getLogger(__name__)


def get_omdb_api_key(key: str | None = None) -> str:
    """Get the OMDB API key from the environment variables or the provided key.

    Args:
        key: The OMDB API key to use.

    Returns:
        The OMDB API key.

    Raises:
        ValueError: If the OMDB API key is not set.
    """
    if key:
        return key
    key = os.getenv("OMDB_API_KEY")
    if not key:
        raise ValueError("OMDB_API_KEY is not set")
    return key


def get_episode_filter_priority(
    episode_id: str | None = None,
    episode_num: int | None = None,
    episode_title: str | None = None,
) -> str:
    """Get the priority episode identifier.

    Priority order: episode_id > episode_num > episode_title

    Args:
        episode_id: The id of the episode to extract.
        episode_num: The number of the episode to extract.
        episode_title: The title of the episode to extract.

    Returns:
        The priority identifier type.
    """
    if episode_id:
        return "episode_id"
    elif episode_num:
        return "episode_num"
    elif episode_title:
        return "episode_title"
    else:
        return ""


def filter_metadata(
    episode_id: str | None = None,
    episode_num: int | None = None,
    episode_title: str | None = None,
    logging_prefix: str | None = None,
    metadata: pl.LazyFrame = METADATA,
) -> pl.LazyFrame:
    """Filter the metadata dataframe based on the episode identifier.

    Args:
        episode_id: The id of the episode to extract.
        episode_num: The number of the episode to extract.
        episode_title: The title of the episode to extract.
        logging_prefix: The prefix to use for logging.
        metadata: The metadata dataframe to filter.

    Returns:
        The filtered metadata dataframe.

    Raises:
        ValueError: If no episode_id, episode_num, or episode_title is provided.
    """

    if not logging_prefix:
        logging_prefix = "data"

    priority = get_episode_filter_priority(episode_id, episode_num, episode_title)

    if priority == "episode_id":
        logger.info(f"Extracting {logging_prefix} for episode_id: {episode_id}")
        df = metadata.filter(pl.col("episode_id") == episode_id)
    elif priority == "episode_num":
        logger.info(f"Extracting {logging_prefix} for episode_num: {episode_num}")
        df = metadata.filter(pl.col("episode_num") == episode_num)
    elif priority == "episode_title":
        logger.info(f"Extracting {logging_prefix} for episode_title: {episode_title}")
        df = metadata.filter(pl.col("episode_title") == episode_title)
    else:
        raise ValueError("No episode_id, episode_num, or episode_title provided")

    return df


def get_episode_ids_from_seasons(
    seasons: int | list[int], metadata: pl.LazyFrame = METADATA
) -> list[str]:
    """Get the episode ids from the seasons.

    Args:
        seasons: The seasons to get the episode ids from.
        metadata: The metadata dataframe to use.

    Returns:
        The episode ids.
    """
    if isinstance(seasons, int):
        seasons = [seasons]

    episode_ids = []
    for season in seasons:
        df = metadata.filter(pl.col("episode_id").str.starts_with(f"S0{season}"))
        episode_ids.extend(df.select("episode_id").collect().to_series().to_list())
    logger.debug(f"Found episode IDs for seasons {seasons}: {episode_ids}")
    return episode_ids


def shift_episode_ids(df: pl.LazyFrame, from_episode_id: str) -> pl.LazyFrame:
    """Shifts episode IDs down by one for all episodes after the given episode in the same season.

    Args:
        df: The dataframe to modify
        from_episode_id: Episode ID in format 'SxxExx' from which to start shifting

    Returns:
        The dataframe with shifted episode IDs
    """
    season = int(from_episode_id[1:3])
    episode = int(from_episode_id[4:6])

    # episodes to shift
    season_match = pl.col("episode_id").str.slice(1, 2).cast(pl.UInt32) == season
    episode_match = pl.col("episode_id").str.slice(4, 2).cast(pl.UInt32) > episode

    # Create new episode ID by decrementing episode number by 1
    new_episode_id = pl.concat_str(
        [
            pl.lit("S"),
            pl.col("episode_id").str.slice(1, 2).str.zfill(2),
            pl.lit("E"),
            (pl.col("episode_id").str.slice(4, 2).cast(pl.UInt32) - 1)
            .cast(pl.Utf8)
            .str.zfill(2),
        ]
    )

    return df.with_columns(
        pl.when(season_match & episode_match)
        .then(new_episode_id)
        .otherwise(pl.col("episode_id"))
        .alias("episode_id")
    )


def shift_episode_nums(df: pl.LazyFrame, from_episode_num: str) -> pl.LazyFrame:
    """Shifts all episode numbers down by one for all episodes after the given episode.

    Args:
        df: The dataframe to modify
        from_episode_num: Episode number from which to start shifting

    Returns:
        The dataframe with shifted episode numbers
    """

    slice = pl.col("episode_num") > from_episode_num
    new_episode_num = pl.col("episode_num") - 1

    return df.with_columns(
        pl.when(slice)
        .then(new_episode_num)
        .otherwise(pl.col("episode_num"))
        .alias("episode_num")
    )


def get_episode_id_num_title(
    df: pl.LazyFrame,
    episode_id: str | None = None,
    episode_num: int | None = None,
    episode_title: str | None = None,
) -> tuple[str, int, str]:
    """Get the episode id, number, and title from the dataframe.

    Args:
        df: The metadata dataframe to get the episode id, number, and title from.
        episode_id: The episode id to get.
        episode_num: The episode number to get.
        episode_title: The episode title to get.

    Raises:
        ValueError: If metadata columns are not coordinated.

    Returns:
        The episode id, number, and title.
    """
    cols = df.collect_schema().names()
    if not all([x in cols for x in ["episode_id", "episode_num", "episode_title"]]):
        raise ValueError("Columns are not coordinated")

    priority = get_episode_filter_priority(episode_id, episode_num, episode_title)

    valid_filter = True
    if priority == "episode_id":
        df = df.filter(pl.col("episode_id") == episode_id)
        if df.collect().height != 1:
            valid_filter = False
        episode_id = episode_id
        episode_num = df.select("episode_num").collect().item()
        episode_title = df.select("episode_title").collect().item()
    elif priority == "episode_num":
        df = df.filter(pl.col("episode_num") == episode_num)
        if df.collect().height != 1:
            valid_filter = False
        episode_id = df.select("episode_id").collect().item()
        episode_title = df.select("episode_title").collect().item()
    elif priority == "episode_title":
        df = df.filter(pl.col("episode_title") == episode_title)
        if df.collect().height != 1:
            valid_filter = False
        episode_id = df.select("episode_id").collect().item()
        episode_num = df.select("episode_num").collect().item()
    else:
        raise ValueError("No episode_id, episode_num, or episode_title provided")

    if not valid_filter:
        raise ValueError(
            f"No episode found with: \n"
            f"episode_id: {episode_id} \n"
            f"episode_num: {episode_num} \n"
            f"episode_title: {episode_title}"
        )

    return episode_id, episode_num, episode_title


def _configure_dict_source(
    source: dict[str, Any]
) -> tuple[str | None, str | None, str | None] | None:
    """Configure dictionary source keys and extract the extractor names.

    Args:
        source: The dictionary source configuration.

    Returns:
        A tuple of (script, credit, rating) extractor names if valid, None otherwise.
    """
    for key, value in source.items():
        if value is not None and key not in ["script", "credit", "rating"]:
            logger.warning(
                f"Invalid extractor: {key}. Must be one of 'script', 'credit', or 'rating'."
            )
            return None

    return (
        source.get("script", None),
        source.get("credit", None),
        source.get("rating", None),
    )



def validate_extractors(source: Source | dict[str, Any]) -> Source:
    """Validate extractors and return a Source dataclass.

    Args:
        source: The Source configuration to validate (either a Source instance or dictionary).

    Returns:
        A validated Source instance.

    Raises:
        ValueError: If the source type is invalid.
        AssertionError: If any of the extractors are invalid.
    """
    if isinstance(source, dict):
        extractors = _configure_dict_source(source)
        if extractors is None:
            raise ValueError("Invalid extractor source dictionary structure")
        script_extractor, credit_extractor, rating_extractor = extractors
        cleaned_source = Source(
            script=script_extractor,
            credit=credit_extractor,
            rating=rating_extractor,
        )
    elif isinstance(source, Source):
        cleaned_source = source
    else:
        raise ValueError("Source must be an instance of Source or a dictionary")

    if not _is_valid_extractors(cleaned_source):
        raise ValueError("Invalid extractor configuration")
    return cleaned_source


def _is_valid_extractors(source: Source) -> bool:
    """Check if the extractors are valid.

    Args:
        source: The Source configuration to validate.

    Returns:
        True if all specified extractors are valid, False otherwise.
    """
    script_extractor = source.script
    credit_extractor = source.credit
    rating_extractor = source.rating

    if script_extractor and script_extractor not in SCRIPT_EXTRACTORS:
        logger.warning(
            f"Invalid script extractor: {script_extractor}. Must be one of {SCRIPT_EXTRACTORS}."
        )
        return False
    if credit_extractor and credit_extractor not in CREDIT_EXTRACTORS:
        logger.warning(
            f"Invalid credit extractor: {credit_extractor}. Must be one of {CREDIT_EXTRACTORS}."
        )
        return False
    if rating_extractor and rating_extractor not in RATING_EXTRACTORS:
        logger.warning(
            f"Invalid rating extractor: {rating_extractor}. Must be one of {RATING_EXTRACTORS}."
        )
        return False

    return True


def is_valid_extractors(source: Source | dict[str, Any]) -> bool:
    """Check if the extractors are valid.

    Args:
        source: The Source configuration to validate (either a Source instance or dictionary).

    Returns:
        True if all specified extractors are valid, False otherwise.
    """
    if not isinstance(source, (Source, dict)):
        raise ValueError("Source must be an instance of Source or a dictionary")
    try:
        validate_extractors(source)
        return True
    except ValueError:
        return False
