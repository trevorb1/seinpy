"""Csv writer."""

from typing import List

from seinpy.base import Exporter
from seinpy.schema import Episode


class CsvExporter(Exporter):
    """Write the data to a csv file."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError