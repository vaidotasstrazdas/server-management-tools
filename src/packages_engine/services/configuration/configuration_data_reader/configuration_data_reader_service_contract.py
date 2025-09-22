from abc import ABC, abstractmethod

from packages_engine.models.configuration import ConfigurationData

class ConfigurationDataReaderServiceContract(ABC):
    @abstractmethod
    def read(self) -> ConfigurationData:
        pass