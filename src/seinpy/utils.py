"""Utility functions for extractors."""

from typing import Optional


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


def get_episode_priority(
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
        raise ValueError("No episode id, number, or title provided")
