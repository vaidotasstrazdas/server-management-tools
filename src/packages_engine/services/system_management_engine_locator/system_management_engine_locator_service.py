"""System Management Engine Locator Service - locates platform-specific engine implementations."""

from packages_engine.services.system_management_engine.engines import LinuxUbuntuEngineService
from packages_engine.services.system_management_engine.system_management_engine_service import (
    SystemManagementEngineService,
)

from .system_management_engine_locator_service_contract import (
    SystemManagementEngineLocatorServiceContract,
)


class SystemManagementEngineLocatorService(SystemManagementEngineLocatorServiceContract):
    """
    Concrete implementation of system management engine locator.

    Currently returns LinuxUbuntuEngineService for all platforms. Future
    implementations may include platform detection and return different
    engines based on the detected operating system.
    """

    def locate_engine(self) -> SystemManagementEngineService:
        """
        Locate and return the appropriate system management engine.

        Currently hardcoded to return LinuxUbuntuEngineService. Future versions
        may implement platform detection.

        Returns:
            LinuxUbuntuEngineService instance for the current platform.
        """
        return LinuxUbuntuEngineService()
