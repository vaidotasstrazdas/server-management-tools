from packages_engine.services.system_management_engine.system_management_engine_service import SystemManagementEngineService

from .system_management_engine_locator_service_contract import SystemManagementEngineLocatorServiceContract

class MockSystemManagementEngineLocatorService(SystemManagementEngineLocatorServiceContract):
    locate_engine_triggered_times = 0
    locate_engine_result: SystemManagementEngineService
    def locate_engine(self) -> SystemManagementEngineService:
        self.locate_engine_triggered_times = self.locate_engine_triggered_times + 1
        return self.locate_engine_result