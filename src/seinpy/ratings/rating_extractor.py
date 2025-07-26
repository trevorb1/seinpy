"""Rating extractor base class."""

from typing import List
from abc import abstractmethod

from seinpy.base import Extractor
from seinpy.schema import Rating


class RatingExtractor(Extractor):
    """Rating extractor base class."""

    def extract(self, data: List) -> List:
        return self.extract_rating()

    @abstractmethod
    def extract_rating(
        self,
    ) -> List[Rating]:
        pass
