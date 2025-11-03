"""Base interface for configuration tasks.

Defines the abstract contract for all system configuration tasks.
"""

from abc import ABC, abstractmethod

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData


class ConfigurationTask(ABC):
    """Abstract base class for system configuration tasks.

    All configuration tasks must implement the configure method to apply
    system configurations based on provided data.
    """

    @abstractmethod
    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Apply configuration to the system.

        Args:
            data: Configuration data containing settings to apply.

        Returns:
            OperationResult[bool]: Success if configured, failure otherwise.
        """
