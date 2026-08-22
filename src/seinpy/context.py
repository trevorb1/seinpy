from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import polars as pl

from seinpy.base import CreditExtractor, Exporter, RatingExtractor, ScriptExtractor
from seinpy.constants import METADATA
from seinpy.credits.empty import EmptyCreditExtractor
from seinpy.credits.omdb import OMDBCreditExtractor
from seinpy.credits.rottentomatoes import RottenTomatoesCreditExtractor
from seinpy.exporters.csv import CsvExporter
from seinpy.exporters.database import DatabaseExporter
from seinpy.exporters.json import JsonExporter
from seinpy.ratings.empty import EmptyRatingExtractor
from seinpy.ratings.omdb import OMDBRatingExtractor
from seinpy.ratings.rottentomatoes import RottenTomatoesRatingExtractor
from seinpy.schema import Episode
from seinpy.scripts.empty import EmptyScriptExtractor
from seinpy.scripts.imsdb import IMDbScriptExtractor
from seinpy.scripts.kaggle import KaggleScriptExtractor
from seinpy.scripts.seinfeldscripts import SeinfeldScriptsExtractor
from seinpy.scripts.seinology import SeinologyScriptExtractor
from seinpy.utils import get_episode_ids_from_seasons, is_valid_extractors

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
        exporter: Exporter | None = None,
    ) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._script_extractor = (
            script_extractor if script_extractor else EmptyScriptExtractor()
        )
        self._credit_extractor = (
            credit_extractor if credit_extractor else EmptyCreditExtractor()
        )
        self._rating_extractor = (
            rating_extractor if rating_extractor else EmptyRatingExtractor()
        )
        self._exporter = exporter

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
    def exporter(self) -> Exporter:
        return self._exporter

    @exporter.setter
    def exporter(self, exporter: Exporter) -> None:
        self._exporter = exporter

    def _get_episode(
        self,
        episode_num: int | None = None,
        episode_title: str | None = None,
        episode_id: str | None = None,
    ) -> Episode:
        """Assemble the episode data."""
        if not any([episode_id, episode_num, episode_title]):
            raise ValueError("No episode number, title, or ID provided")
        script = self._script_extractor.extract(episode_id, episode_num, episode_title)
        credit = self._credit_extractor.extract(episode_id, episode_num, episode_title)
        rating = self._rating_extractor.extract(episode_id, episode_num, episode_title)
        return Episode(script=script, credit=credit, rating=rating)

    def _get_episodes(
        self,
        episode_nums: int | list[int] | None = None,
        episode_titles: str | list[str] | None = None,
        episode_ids: str | list[str] | None = None,
        seasons: int | list[int] | None = None,
        metadata: pl.LazyFrame = METADATA,
    ) -> list[Episode]:
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
            episode_ids = get_episode_ids_from_seasons(seasons, metadata)
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
        episode_nums: int | list[int] | None = None,
        episode_titles: str | list[str] | None = None,
        episode_ids: str | list[str] | None = None,
        seasons: int | list[int] | None = None,
        get_all: bool = False,
        metadata: pl.LazyFrame = METADATA,
    ) -> list[Episode]:
        """Read the data from the file."""

        if isinstance(episode_nums, int):
            episode_nums = [episode_nums]
        if isinstance(episode_titles, str):
            episode_titles = [episode_titles]
        if isinstance(episode_ids, str):
            episode_ids = [episode_ids]
        if isinstance(seasons, int):
            seasons = [seasons]

        if (
            not any([episode_nums, episode_titles, episode_ids, seasons])
            and not get_all
        ):
            raise ValueError("No episode number, title, ID, or season provided")

        if get_all:
            logger.info("Reading all episodes")
            ids = (
                metadata.select(pl.col("episode_id"))
                .unique()
                .collect()
                .to_series()
                .to_list()
            )
            return self._get_episodes(episode_ids=ids, metadata=metadata)
        else:
            logger.info(
                f"Reading episodes:\n Num: {episode_nums}\n Title: {episode_titles}\n ID: {episode_ids}\n Seasons: {seasons}"
            )
            return self._get_episodes(
                episode_nums=episode_nums,
                episode_titles=episode_titles,
                episode_ids=episode_ids,
                seasons=seasons,
                metadata=metadata,
            )

    def write(
        self,
        data: list[Episode],
        save_path: str,
    ) -> None:
        """Export the data to a file."""
        if not self._exporter:
            raise ValueError("Must provide an exporter")
        self._exporter.export(data=data, save_path=save_path)

    def read_and_write(self, **kwargs: dict[str, Any]) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        if not self._exporter:
            raise ValueError("Must provide an exporter")
        episodes = self.read(**kwargs)
        try:
            save_path = kwargs["save_path"]
        except KeyError:
            raise ValueError("Save path not provided")
        self.write(episodes, save_path)


################################################
# Helpers for assigning extractors and exporters
################################################


def _get_script_extractor(source: str | None, **kwargs: Any) -> ScriptExtractor:
    """Get the script extractor for the given source."""
    if source is None or source == "empty":
        return EmptyScriptExtractor()
    elif source == "kaggle":
        return KaggleScriptExtractor()
    elif source == "imdb":
        return IMDbScriptExtractor()
    elif source == "seinfeldscripts":
        return SeinfeldScriptsExtractor()
    elif source == "seinology":
        return SeinologyScriptExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_credit_extractor(source: str | None, **kwargs: Any) -> CreditExtractor:
    """Get the credit extractor for the given source."""
    if source is None or source == "empty":
        return EmptyCreditExtractor()
    elif source == "omdb":
        omdb_api_key = kwargs.get("omdb_api_key", None)
        return OMDBCreditExtractor(omdb_api_key=omdb_api_key)
    elif source == "rottentomatoes":
        return RottenTomatoesCreditExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_rating_extractor(source: str | None, **kwargs: Any) -> RatingExtractor:
    """Get the rating extractor for the given source."""
    if source is None or source == "empty":
        return EmptyRatingExtractor()
    elif source == "omdb":
        omdb_api_key = kwargs.get("omdb_api_key", None)
        return OMDBRatingExtractor(omdb_api_key=omdb_api_key)
    elif source == "rottentomatoes":
        return RottenTomatoesRatingExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_exporter(save_type: str, **kwargs: Any) -> Exporter:
    """Get the exporter for the given save type."""
    if save_type == "database":
        return DatabaseExporter(**kwargs)
    elif save_type == "csv":
        return CsvExporter(**kwargs)
    elif save_type == "json":
        return JsonExporter(**kwargs)
    else:
        raise ValueError(f"Invalid save type: {save_type}")


##################
# Public Interface
##################


def read_episodes(
    source: dict[str, Any],
    episode_ids: str | list[str] | None = None,
    episode_nums: int | list[int] | None = None,
    episode_titles: str | list[str] | None = None,
    seasons: int | list[int] | None = None,
    get_all: bool = False,
    **kwargs: Any,
) -> list[Episode]:
    """Read the episodes from the given source.

    Args:
        source: A dictionary containing the sources for the script, credit, and rating extractors.
            "script": The source for the script extractor.
            "credit": The source for the credit extractor.
            "rating": The source for the rating extractor.
        episode_ids: The IDs of the episodes to read.
        episode_nums: The numbers of the episodes to read.
        episode_titles: The titles of the episodes to read.
        seasons: The seasons of the episodes to read.
        get_all: Whether to read all episodes. Defaults to False.

    kwargs:
        omdb_api_key: Needed for the OMDB extractors.

    Returns:
        A list of episodes.

    Notes:
    - Only one of episode_ids, episode_nums, episode_titles, or seasons needs to be provided.
    - If get_all is True, all episodes will be read.
    - At least one source must be provided. If any of 'script', 'credit', or 'rating' are not provided, an empty extractor will be used.

    Example:
        >>> read_episodes(source={"script": "kaggle", "credit": "omdb", "rating": "omdb"}, episode_ids=["S01E01"])
        [
            Episode(
                script=Script(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Episode 1"
                    ),
                    script_lines=[
                        ScriptLine(
                            speaker="Jerry",
                            dialogue="Hi, I'm Jerry."
                        ),
                        ScriptLine(
                            speaker="George",
                            dialogue="Hi, I'm George."
                        ),
                        ...
                    )],
                credit=Credit(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Episode 1"
                    ),
                    description="Seinfeld is literally a show about nothing.",
                    date="2025-01-01",
                    writers=[
                        Writer(name="Larry David"),
                        Writer(name="Jerry Seinfeld")
                    ],
                    directors=[
                        Director(name="Jerry Seinfeld"),
                        Director(name="Larry David")
                    ],
                    actors=[
                        Actor(name="Jerry Seinfeld", role="Jerry"),
                        Actor(name="Jason Alexander", role="George"),
                        Actor(name="Julia Louis-Dreyfus", role="Elaine"),
                        Actor(name="Michael Richards", role="Kramer")
                    ]
                ),
                rating=Rating(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Episode 1"
                    ),
                    rating=10,
                    num_votes=100,
                    link="https://www.imdb.com/"
                )
            )
        ]
    """

    assert is_valid_extractors(source)

    script = _get_script_extractor(source.get("script", None), **kwargs)
    credit = _get_credit_extractor(source.get("credit", None), **kwargs)
    rating = _get_rating_extractor(source.get("rating", None), **kwargs)
    context = Context(
        script_extractor=script, credit_extractor=credit, rating_extractor=rating
    )

    metadata = kwargs.get("metadata", METADATA)  # jsut for tests

    return context.read(
        episode_ids=episode_ids,
        episode_nums=episode_nums,
        episode_titles=episode_titles,
        seasons=seasons,
        get_all=get_all,
        metadata=metadata,
    )


def write_episodes(
    save_type: str,
    save_path: str,
    data: list[Episode],
) -> None:
    save_path = Path(save_path)
    if save_type == "database":
        if save_path.suffix != ".db":
            raise ValueError("Save path must end with .db")
    elif save_type == "csv":
        if save_path.suffix != ".csv":
            raise ValueError("Save path must end with .csv")
    elif save_type == "json":
        if save_path.suffix != ".json":
            raise ValueError("Save path must end with .json")
    else:
        raise ValueError(f"Invalid save type: {save_type}")

    exporter = _get_exporter(save_type)
    return exporter.export(data, save_path)
