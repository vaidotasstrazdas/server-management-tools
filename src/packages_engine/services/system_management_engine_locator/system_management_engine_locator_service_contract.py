"""System Management Engine Locator Service Contract - defines interface for engine location."""

from abc import ABC, abstractmethod

from packages_engine.services.system_management_engine.system_management_engine_service import (
    SystemManagementEngineService,
)


class SystemManagementEngineLocatorServiceContract(ABC):
    """
    Abstract base class defining the contract for system management engine locator services.

    Provides a method to locate and return the appropriate system management engine
    for the current platform (e.g., Linux Ubuntu, other distributions, etc.).
    """

    @abstractmethod
    def locate_engine(self) -> SystemManagementEngineService:
        """
        Locate and return the appropriate system management engine for the current platform.

        Returns:
            SystemManagementEngineService instance for the detected platform.
        """
