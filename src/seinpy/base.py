"""Base classes for extractors and writers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from seinpy.schema import Episode


class Extractor(ABC):
    """Base strategy class for all extractors."""

    @abstractmethod
    def extract(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> List[Episode]:
        """Extract all data from the given episode.

        Args:
            episode_num: The number of the episode to extract.
            episode_title: The title of the episode to extract.
            episode_id: The id of the episode to extract.

        Returns:
            A list of episodes.

        Raises:
            ValueError: If the episode does not exist.

        Notes:
            - Only need to provide one of episode_num, episode_title, or episode_id.
            - If multiple are provided, the priority is episode_id, then episode_num, then episode_title.
        """
        pass

    def check_episode_exists(
        self,
        episode_id: str | None = None,
        episode_num: int | None = None,
        episode_title: str | None = None,
    ) -> bool:
        """Check if the episode exists.

        Args:
            epispde_id: The id of the episode to check.
            episode_num: The number of the episode to check.
            episode_title: The title of the episode to check.

        Returns:
            True if the episode exists, False otherwise.
        """
        if episode_id:
            return self._episode_id_exists(episode_id)
        elif episode_num:
            return self._episode_num_exists(episode_num)
        elif episode_title:
            return self._episode_title_exists(episode_title)
        else:
            raise ValueError("No episode id, number, or title provided")

    def _episode_id_exists(self, episode_id: str) -> bool:
        """Check if the episode id exists.

        Args:
            episode_id: The id of the episode to check.
        """
        raise NotImplementedError

    def _episode_num_exists(self, episode_num: int) -> bool:
        """Check if the episode number exists.

        Args:
            episode_nums: The number of the episode to check.
        """
        raise NotImplementedError

    def _episode_title_exists(self, episode_title: str) -> bool:
        """Check if the episode title exists.

        Args:
            episode_titles: The title of the episode to check.
        """
        raise NotImplementedError


class Writer(ABC):
    """Base strategy class for all writers."""

    @abstractmethod
    def write(
        self,
        data: List[Episode],
    ) -> None:
        """Write the data to the file.

        Args:
            data: The episode data to write.
        """
        pass
