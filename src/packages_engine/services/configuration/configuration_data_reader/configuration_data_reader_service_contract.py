"""Imports for the interface definition."""

from abc import ABC, abstractmethod

from packages_engine.models.configuration import ConfigurationData


class ConfigurationDataReaderServiceContract(ABC):
    """Interface defintion."""

    @abstractmethod
    def read(self, stored: ConfigurationData | None = None) -> ConfigurationData:
        """Method to read the configuration data."""

    @abstractmethod
    def load_stored(self) -> ConfigurationData | None:
        """Method to load stored configuration data."""
