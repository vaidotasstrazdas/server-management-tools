from abc import ABC, abstractmethod

from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

class ContentReader(ABC):
    @abstractmethod
    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        pass