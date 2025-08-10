"""Utility functions for extractors."""

from typing import Optional

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
