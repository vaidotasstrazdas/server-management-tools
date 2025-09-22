from abc import ABC, abstractmethod

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

class ConfigurationTask(ABC):
    @abstractmethod
    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        pass