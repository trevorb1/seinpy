"""Csv writer."""

from typing import List

from seinpy.main import Writer
from seinpy.schema import Episode


class CsvWriter(Writer):
    """Write the data to a csv file."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError