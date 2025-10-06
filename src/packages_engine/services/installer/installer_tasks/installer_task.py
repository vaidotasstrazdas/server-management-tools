"""Necessary imports to configure the interface for the installer task."""
from abc import ABC, abstractmethod
from packages_engine.models import OperationResult


class InstallerTask(ABC):
    """Contract definitions of the interface."""

    @abstractmethod
    def install(self) -> OperationResult[bool]:
        """Method that each task class inheriting this interface must implement."""
