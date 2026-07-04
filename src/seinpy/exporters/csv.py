"""Csv writer."""

from functools import reduce
from typing import List

from seinpy.base import Exporter
from seinpy.schema import Credit, Episode, EpisodeRef, Rating, Script

import polars as pl


class CsvExporter(Exporter):
    """Write the data to a csv file."""

    def __eq__(self, other: object) -> bool:
        """Check equality with another CsvExporter instance."""
        if not isinstance(other, CsvExporter):
            return NotImplemented
        return True

    @staticmethod
    def _episode_ref_to_dataframe(episode_ref: EpisodeRef) -> pl.LazyFrame:
        """Convert an episode reference to a dataframe."""
        data = {}
        for key, value in episode_ref.model_dump().items():
            data[key] = [value]
        return pl.LazyFrame(data)

    @staticmethod
    def _script_to_dataframe(script: Script) -> pl.LazyFrame:
        """Convert a script to a dataframe."""
        num_lines = len(script.script_lines)
        data = {}
        for key, value in script.model_dump().items():
            if key == "script_lines":
                data["speaker"] = [x["speaker"] for x in value]
                data["dialogue"] = [x["dialogue"] for x in value]
            elif key == "ref":
                # quicker than calling _episode_ref_to_dataframe and joining dfs
                for sub_key, sub_value in value.items():
                    data[sub_key] = [sub_value] * num_lines
            else:
                data[key] = [value] * num_lines
        return pl.LazyFrame(data)

    @staticmethod
    def _credit_to_dataframe(credit: Credit) -> pl.LazyFrame:
        """Convert a credit to a dataframe."""
        data = {}
        for key, value in credit.model_dump().items():
            if key == "ref":
                # quicker than calling _episode_ref_to_dataframe and joining dfs
                for sub_key, sub_value in value.items():
                    data[sub_key] = [sub_value]
            elif key in ["writers", "directors", "actors"]:
                joined_names = []
                for sub_value in value:
                    # append all info on one credit together (ie. actor|role)
                    joined_names.append("|".join(sub_value.values()))
                # append all info on all credits together (ie. actor1;actor2)
                data[key] = [";".join(joined_names)]
            else:
                data[key] = [value]
        return pl.LazyFrame(data)

    @staticmethod
    def _rating_to_dataframe(rating: Rating) -> pl.LazyFrame:
        """Convert a rating to a dataframe."""
        data = {}
        for key, value in rating.model_dump().items():
            if key == "ref":
                # quicker than calling _episode_ref_to_dataframe and joining dfs
                for sub_key, sub_value in value.items():
                    data[sub_key] = [sub_value]
            else:
                data[key] = [value]
        return pl.LazyFrame(data)

    def convert_to_dataframe(self, episodes: List[Episode] | Episode) -> pl.LazyFrame:
        """Convert the data to a dataframe."""

        if isinstance(episodes, Episode):
            episodes = [episodes]
        elif isinstance(episodes, List):
            if not all(isinstance(episode, Episode) for episode in episodes):
                raise ValueError("Data must be a list of episodes")
        else:
            raise ValueError("Data must be a list of episodes or a single episode")

        dfs_to_concat = []
        cols_to_join_on = episodes[0].script.ref.model_dump().keys()
        for episode in episodes:
            dfs = [
                self._script_to_dataframe(episode.script),
                self._credit_to_dataframe(episode.credit),
                self._rating_to_dataframe(episode.rating),
            ]
            dfs_to_concat.append(
                reduce(
                    lambda left, right: left.join(
                        right, how="inner", on=cols_to_join_on
                    ),
                    dfs,
                )
            )

        return pl.concat(dfs_to_concat)

    def export(self, data: List[Episode], save_path: str) -> None:
        df = self.convert_to_dataframe(data).collect()
        df.write_csv(save_path)
