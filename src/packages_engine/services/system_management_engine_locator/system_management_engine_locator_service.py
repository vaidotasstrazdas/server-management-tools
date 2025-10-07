from packages_engine.services.system_management_engine.engines import LinuxUbuntuEngineService
from packages_engine.services.system_management_engine.system_management_engine_service import (
    SystemManagementEngineService,
)

from .system_management_engine_locator_service_contract import (
    SystemManagementEngineLocatorServiceContract,
)


class SystemManagementEngineLocatorService(SystemManagementEngineLocatorServiceContract):
    def locate_engine(self) -> SystemManagementEngineService:
        return LinuxUbuntuEngineService()
