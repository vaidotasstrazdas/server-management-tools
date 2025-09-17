from abc import ABC, abstractmethod

from packages_engine.services.system_management_engine.system_management_engine_service import SystemManagementEngineService

class SystemManagementEngineLocatorServiceContract(ABC):
    @abstractmethod
    def locate_engine(self) -> SystemManagementEngineService:
        pass