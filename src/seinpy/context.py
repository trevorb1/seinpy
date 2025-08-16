from __future__ import annotations
from typing import List
from seinpy.schema import Episode
from seinpy.base import ScriptExtractor, CreditExtractor, RatingExtractor
from seinpy.base import Writer
from seinpy.utils import get_episode_ids_from_seasons
import logging

logger = logging.getLogger(__name__)


class Context:
    """
    The Context defines the interface of interest to clients.
    """

    def __init__(
        self,
        script_extractor: ScriptExtractor,
        credit_extractor: CreditExtractor,
        rating_extractor: RatingExtractor,
        writer: Writer | None = None,
    ) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """

        self._script_extractor = script_extractor
        self._credit_extractor = credit_extractor
        self._rating_extractor = rating_extractor
        self._writer = writer

    @property
    def script_extractor(self) -> ScriptExtractor:
        return self._script_extractor

    @script_extractor.setter
    def script_extractor(self, script_extractor: ScriptExtractor) -> None:
        self._script_extractor = script_extractor

    @property
    def credit_extractor(self) -> CreditExtractor:
        return self._credit_extractor

    @credit_extractor.setter
    def credit_extractor(self, credit_extractor: CreditExtractor) -> None:
        self._credit_extractor = credit_extractor

    @property
    def rating_extractor(self) -> RatingExtractor:
        return self._rating_extractor

    @rating_extractor.setter
    def rating_extractor(self, rating_extractor: RatingExtractor) -> None:
        self._rating_extractor = rating_extractor

    @property
    def writer(self) -> Writer:
        return self._writer

    @writer.setter
    def writer(self, writer: Writer) -> None:
        self._writer = writer

    def _get_episode(
        self,
        episode_num: int | None = None,
        episode_title: str | None = None,
        episode_id: str | None = None,
    ) -> Episode:
        """Assemble the episode data."""
        script = self._script_extractor.extract(episode_id, episode_num, episode_title)
        credit = self._credit_extractor.extract(episode_id, episode_num, episode_title)
        rating = self._rating_extractor.extract(episode_id, episode_num, episode_title)
        return Episode(script=script, credit=credit, rating=rating)

    def _get_episodes(
        self,
        episode_nums: int | List[int] | None = None,
        episode_titles: str | List[str] | None = None,
        episode_ids: str | List[str] | None = None,
        seasons: int | List[int] | None = None,
    ) -> List[Episode]:
        """Assemble the episode data."""
        if episode_nums:
            logger.info(f"Reading episode numbers: {episode_nums}")
            return [
                self._get_episode(episode_num=episode_num)
                for episode_num in episode_nums
            ]
        elif episode_titles:
            logger.info(f"Reading episode titles: {episode_titles}")
            return [
                self._get_episode(episode_title=episode_title)
                for episode_title in episode_titles
            ]
        elif seasons:
            logger.info(f"Reading seasons: {seasons}")
            episode_ids = get_episode_ids_from_seasons(seasons)
            return [
                self._get_episode(episode_id=episode_id) for episode_id in episode_ids
            ]
        elif episode_ids:
            logger.info(f"Reading episode IDs: {episode_ids}")
            return [
                self._get_episode(episode_id=episode_id) for episode_id in episode_ids
            ]
        else:
            raise ValueError("No episode number, title, or season provided")

    def read(
        self,
        episode_nums: int | List[int] | None = None,
        episode_titles: str | List[str] | None = None,
        episode_ids: str | List[str] | None = None,
        seasons: int | List[int] | None = None,
        get_all: bool = False,
    ) -> List[Episode]:
        """Read the data from the file."""

        if isinstance(episode_nums, int):
            episode_nums = [episode_nums]
        if isinstance(episode_titles, str):
            episode_titles = [episode_titles]
        if isinstance(episode_ids, str):
            episode_ids = [episode_ids]
        if isinstance(seasons, int):
            seasons = [seasons]

        if get_all:
            logger.info("Reading all episodes")
            return self._get_episodes()
        else:
            logger.info(
                f"Reading episodes:\n Num: {episode_nums}\n Title: {episode_titles}\n ID: {episode_ids}\n Seasons: {seasons}"
            )
            return self._get_episodes(
                episode_nums=episode_nums,
                episode_titles=episode_titles,
                episode_ids=episode_ids,
                seasons=seasons,
            )

    def read_and_write(self) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        raise NotImplementedError


if __name__ == "__main__":
    # The client code picks a concrete strategy and passes it to the context.
    # The client should be aware of the differences between strategies in order
    # to make the right choice.

    context = Context(
        ScriptExtractor(),
        CreditExtractor(),
        RatingExtractor(),
    )
    print("Client: Strategy is set to normal sorting.")
    context.do_some_business_logic()
