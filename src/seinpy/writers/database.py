"""Database writer."""

from typing import List

from seinpy.main import Writer
from seinpy.schema import Episode


class DatabaseWriter(Writer):
    """Write the data to a database."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError