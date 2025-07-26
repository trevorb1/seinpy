"""Credit extractor base class."""

from typing import List
from abc import abstractmethod

from seinpy.base import Extractor
from seinpy.schema import Credit


class CreditExtractor(Extractor):
    """Credit extractor base class."""

    def extract(self, data: List) -> List[Credit]:
        return self.extract_credit()

    @abstractmethod
    def extract_credit(
        self,
    ) -> List[Credit]:
        pass
