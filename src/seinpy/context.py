from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import polars as pl

from seinpy.base import (
    CreditExtractor,
    Exporter,
    RatingExtractor,
    ScriptExtractor,
    Source,
)
from seinpy.constants import (
    METADATA,
    CreditSource,
    ExporterType,
    RatingSource,
    ScriptSource,
)
from seinpy.credits.empty import EmptyCreditExtractor
from seinpy.credits.omdb import OMDBCreditExtractor
from seinpy.credits.rottentomatoes import RottenTomatoesCreditExtractor
from seinpy.exporters.csv import CsvExporter
from seinpy.exporters.database import DatabaseExporter
from seinpy.exporters.json import JsonExporter
from seinpy.ratings.empty import EmptyRatingExtractor
from seinpy.ratings.omdb import OMDBRatingExtractor
from seinpy.ratings.rottentomatoes import RottenTomatoesRatingExtractor
from seinpy.schema import Credit, Episode, Rating, Script
from seinpy.scripts.empty import EmptyScriptExtractor
from seinpy.scripts.imsdb import IMDbScriptExtractor
from seinpy.scripts.kaggle import KaggleScriptExtractor
from seinpy.scripts.seinfeldscripts import SeinfeldScriptsExtractor
from seinpy.scripts.seinology import SeinologyScriptExtractor
from seinpy.utils import get_episode_ids_from_seasons, validate_extractors

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

    def _extract(
        self,
        data_source: str,
        episode_num: int | None = None,
        episode_title: str | None = None,
        episode_id: str | None = None,
    ) -> Script | Credit | Rating | None:
        """Extract the episode data for a specific source component.

        Args:
            data_source: The component name to extract ("script", "credit", or "rating").
            episode_num: The episode number to extract.
            episode_title: The title of the episode to extract.
            episode_id: The ID of the episode to extract.

        Returns:
            The extracted data object or None if extraction fails.
        """
        register = {
            "script": self._script_extractor,
            "credit": self._credit_extractor,
            "rating": self._rating_extractor,
        }

        try:
            return register[data_source].extract(
                episode_id=episode_id,
                episode_num=episode_num,
                episode_title=episode_title,
            )
        except ValueError as e:
            logger.warning(
                f"Could not extract {data_source} for {episode_id or episode_num or episode_title}: {e}"
            )
            return None

    def _get_episode(
        self,
        episode_num: int | None = None,
        episode_title: str | None = None,
        episode_id: str | None = None,
    ) -> Episode:
        """Assemble the episode data."""
        if not any([episode_id, episode_num, episode_title]):
            raise ValueError("No episode number, title, or ID provided")

        script = self._extract(
            "script",
            episode_num=episode_num,
            episode_title=episode_title,
            episode_id=episode_id,
        )
        credit = self._extract(
            "credit",
            episode_num=episode_num,
            episode_title=episode_title,
            episode_id=episode_id,
        )
        rating = self._extract(
            "rating",
            episode_num=episode_num,
            episode_title=episode_title,
            episode_id=episode_id,
        )

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
                .sort("episode_id")
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


def _get_script_extractor(
    source: ScriptSource | str | None, **kwargs: Any
) -> ScriptExtractor:
    """Get the script extractor for the given source."""
    if source is None or source == "empty":
        return EmptyScriptExtractor()
    elif source == ScriptSource.KAGGLE:
        return KaggleScriptExtractor()
    elif source == ScriptSource.IMDB:
        return IMDbScriptExtractor()
    elif source == ScriptSource.SEINFELDSCRIPTS:
        return SeinfeldScriptsExtractor()
    elif source == ScriptSource.SEINOLOGY:
        return SeinologyScriptExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_credit_extractor(
    source: CreditSource | str | None, **kwargs: Any
) -> CreditExtractor:
    """Get the credit extractor for the given source."""
    if source is None or source == "empty":
        return EmptyCreditExtractor()
    elif source == CreditSource.OMDB:
        omdb_api_key = kwargs.get("omdb_api_key", None)
        return OMDBCreditExtractor(omdb_api_key=omdb_api_key)
    elif source == CreditSource.ROTTENTOMATOES:
        return RottenTomatoesCreditExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_rating_extractor(
    source: RatingSource | str | None, **kwargs: Any
) -> RatingExtractor:
    """Get the rating extractor for the given source."""
    if source is None or source == "empty":
        return EmptyRatingExtractor()
    elif source == RatingSource.OMDB:
        omdb_api_key = kwargs.get("omdb_api_key", None)
        return OMDBRatingExtractor(omdb_api_key=omdb_api_key)
    elif source == RatingSource.ROTTENTOMATOES:
        return RottenTomatoesRatingExtractor()
    else:
        raise ValueError(f"Invalid source: {source}")


def _get_exporter(save_type: ExporterType | str, **kwargs: Any) -> Exporter:
    """Get the exporter for the given save type."""
    if save_type == ExporterType.DATABASE:
        return DatabaseExporter(**kwargs)
    elif save_type == ExporterType.CSV:
        return CsvExporter(**kwargs)
    elif save_type == ExporterType.JSON:
        return JsonExporter(**kwargs)
    else:
        raise ValueError(f"Invalid save type: {save_type}")


##################
# Public Interface
##################


def read_episodes(
    source: Source | dict[str, Any],
    episode_ids: str | list[str] | None = None,
    episode_nums: int | list[int] | None = None,
    episode_titles: str | list[str] | None = None,
    seasons: int | list[int] | None = None,
    get_all: bool = False,
    **kwargs: Any,
) -> list[Episode]:
    """Read the episodes from the given source.

    Args:
        source: A Source instance or dictionary containing the configurations for the script, credit, and rating extractors.
        episode_ids: The IDs of the episodes to read.
        episode_nums: The numbers of the episodes to read.
        episode_titles: The titles of the episodes to read.
        seasons: The seasons of the episodes to read.
        get_all: Whether to read all episodes. Defaults to False.

    kwargs:
        omdb_api_key: Needed for the OMDB extractors.

    Returns:
        A list of Episode objects.

    Examples:
        >>> from seinpy import read_episodes, Source
        >>> source = Source(script="kaggle")
        >>> read_episodes(source=source, seasons=[1], episode_nums=[1])
        [
            Episode(
                id="S01E01",
                season=1,
                episode_num=1,
                episode_title="Good News, Bad News",
                script=Script(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Good News, Bad News"
                    ),
                    lines=[
                        ScriptLine(speaker="Jerry", dialogue="It's a good news, bad news scenario...")
                    ]
                ),
                credit=Credit(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Good News, Bad News"
                    ),
                    writers=[Writer(name="Larry David"), Writer(name="Jerry Seinfeld")],
                    directors=[Director(name="Art Wolff")],
                    actors=[
                        Actor(name="Jerry Seinfeld", role="Jerry"),
                        Actor(name="Jason Alexander", role="George"),
                        Actor(name="Michael Richards", role="Kramer")
                    ]
                ),
                rating=Rating(
                    ref=EpisodeRef(
                        episode_id="S01E01",
                        episode_num=1,
                        episode_title="Good News, Bad News"
                    ),
                    rating=10,
                    num_votes=100,
                    link="https://www.imdb.com/"
                )
            )
        ]
    """

    source = validate_extractors(source)

    script = _get_script_extractor(source.script, **kwargs)
    credit = _get_credit_extractor(source.credit, **kwargs)
    rating = _get_rating_extractor(source.rating, **kwargs)
    context = Context(
        script_extractor=script, credit_extractor=credit, rating_extractor=rating
    )

    metadata = kwargs.get("metadata", METADATA)  # just for tests

    return context.read(
        episode_ids=episode_ids,
        episode_nums=episode_nums,
        episode_titles=episode_titles,
        seasons=seasons,
        get_all=get_all,
        metadata=metadata,
    )


def write_episodes(
    save_type: ExporterType | str,
    save_path: str,
    data: list[Episode],
) -> None:
    """Export episode data to a file or database.

    Args:
        save_type: The format or target storage type. Supported values are
            ExporterType members or strings.
        save_path: The file path where the exported episodes will be saved.
            Must end with the corresponding file extension (.db, .csv, or .json).
        data: A list of Episode objects to export.
    """
    save_path = Path(save_path)
    if save_type == ExporterType.DATABASE:
        if save_path.suffix != ".db":
            raise ValueError("Save path must end with .db")
    elif save_type == ExporterType.CSV:
        if save_path.suffix != ".csv":
            raise ValueError("Save path must end with .csv")
    elif save_type == ExporterType.JSON:
        if save_path.suffix != ".json":
            raise ValueError("Save path must end with .json")
    else:
        raise ValueError(f"Invalid save type: {save_type}")

    exporter = _get_exporter(save_type)
    return exporter.export(data, save_path)
