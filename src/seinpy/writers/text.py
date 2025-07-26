"""Text writer."""

from typing import List

from seinpy.main import Writer
from seinpy.schema import Episode


class TxtWriter(Writer):
    """Write the data to a txt file."""

    def write(self, data: List[Episode], save_path: str) -> None:
        raise NotImplementedError
