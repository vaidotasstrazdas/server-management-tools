from abc import ABC, abstractmethod

from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models import OperationResult

class ConfigurationContentReaderServiceContract(ABC):
    @abstractmethod
    def read(self, content: ConfigurationContent, config: ConfigurationData, template_path: Optional[str] = None) -> OperationResult[str]:
        pass