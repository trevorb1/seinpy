"""Json writer."""

import json

from seinpy.base import Exporter
from seinpy.schema import Episode


class JsonExporter(Exporter):
    """Write the data to a json file."""

    def __eq__(self, other: object) -> bool:
        """Check equality with another JsonExporter instance."""
        if not isinstance(other, JsonExporter):
            return False
        return True

    @staticmethod
    def convert_to_json(episodes: list[Episode] | Episode) -> list[dict]:
        """Convert the data to a json string."""
        if isinstance(episodes, Episode):
            episodes = [episodes]
        elif isinstance(episodes, list):
            if not all(isinstance(episode, Episode) for episode in episodes):
                raise ValueError("Data must be a list of episodes")
        else:
            raise ValueError("Data must be a list of episodes or a single episode")

        all_data = []
        for episode in episodes:
            data = {}
            episode_data = episode.model_dump()

            # ref will be the same for all episodes
            for _, values in episode_data.items():
                # ref may not be present if credit or rating or data is empty
                if values["ref"]:
                    data["ref"] = values["ref"]
                    continue

            # remove ref from all other data
            episode_data_copy = episode_data.copy()
            for item in episode_data_copy:
                episode_data[item].pop("ref")

            # add all other data to the data dictionary
            for key, value in episode_data.items():
                data[key] = value

            all_data.append(data)

        return all_data

    def export(self, data: list[Episode], save_path: str) -> None:
        json_data = self.convert_to_json(data)
        with open(save_path, "w") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
