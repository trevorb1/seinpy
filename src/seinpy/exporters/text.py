"""Text writer."""

from typing import List

from seinpy.base import Exporter
from seinpy.schema import Episode


class TxtExporter(Exporter):
    """Write the data to a txt file."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError
