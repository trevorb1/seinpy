"""Json writer."""

from typing import List

from seinpy.base import Exporter
from seinpy.schema import Episode


class JsonExporter(Exporter):
    """Write the data to a json file."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError