"""Utility functions for extractors."""

from typing import Optional
import os
from seinpy.constants import METADATA
import polars as pl
import logging

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
    else:
        key = os.getenv("OMDB")
    if key is None:
        raise ValueError("OMDB_API_KEY is not set")
    return key


def validate_episode_parameters(
    episode_id: Optional[str] = None,
    episode_num: Optional[int] = None,
    episode_title: Optional[str] = None,
) -> None:
    """Validate that at least one episode identifier is provided.

    Args:
        episode_id: The id of the episode to extract.
        episode_num: The number of the episode to extract.
        episode_title: The title of the episode to extract.

    Raises:
        ValueError: If no episode identifier is provided.
    """
    if not any([episode_id, episode_num, episode_title]):
        raise ValueError("No episode id, number, or title provided")


def get_episode_filter_priority(
    episode_id: Optional[str] = None,
    episode_num: Optional[int] = None,
    episode_title: Optional[str] = None,
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
    extractor_name: str | None = None,
) -> pl.DataFrame:
    """Filter the metadata dataframe based on the episode identifier.

    Args:
        priority: The priority of the episode identifier.
        episode_id: The id of the episode to extract.
        episode_num: The number of the episode to extract.
        episode_title: The title of the episode to extract.
        extractor_name: The name of the extractor.

    Returns:
        The filtered metadata dataframe.
    """
    
    if not extractor_name:
        extractor_name = "data"
    
    priority = get_episode_filter_priority(episode_id, episode_num, episode_title)
    
    if priority == "episode_id":
        logger.info(f"Extracting {extractor_name} for episode_id: {episode_id}")
        df = METADATA.filter(pl.col("episode_id") == episode_id)
    elif priority == "episode_num":
        logger.info(f"Extracting {extractor_name} for episode_num: {episode_num}")
        df = METADATA.filter(pl.col("episode_num") == episode_num)
    elif priority == "episode_title":
        logger.info(f"Extracting {extractor_name} for episode_title: {episode_title}")
        df = METADATA.filter(pl.col("episode_title") == episode_title)
    else:
        raise ValueError("No episode_id, episode_num, or episode_title provided")

    return df