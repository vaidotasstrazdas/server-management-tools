"""Imports for the configuration task interface."""

from abc import ABC, abstractmethod

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData


class ConfigurationTask(ABC):
    """Contract for the interface"""

    @abstractmethod
    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Method that each class implementing this interface must implement."""
