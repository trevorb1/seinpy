"""Database writer."""

from typing import List

from seinpy.base import Exporter
from seinpy.schema import Episode


class DatabaseExporter(Exporter):
    """Write the data to a database."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError