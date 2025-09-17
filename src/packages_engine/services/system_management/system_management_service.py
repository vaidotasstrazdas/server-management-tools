from typing import Optional

from packages_engine.services.system_management_engine import SystemManagementEngineService

from packages_engine.models.operation_result import OperationResult

from .system_management_service_contract import SystemManagementServiceContract

class SystemManagementService(SystemManagementServiceContract):
    engine: SystemManagementEngineService
    def __init__(self, engine: SystemManagementEngineService):
        self.engine = engine

    def is_installed(self, package: str) -> bool:
        return self.engine.is_installed(package)
    
    def install(self, package: str) -> OperationResult[bool]:
        return self.engine.install(package)
    
    def is_running(self, package: str) -> OperationResult[bool]:
        return self.engine.is_running(package)

    def start(self, package: str) -> OperationResult[bool]:
        return self.engine.start(package)

    def restart(self, package: str) -> OperationResult[bool]:
        return self.engine.restart(package)

    def execute_command(self, command: list[str], directory: Optional[str] = None) -> OperationResult[bool]:
        return self.engine.execute_command(command, directory)

    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        return self.engine.execute_raw_command(command)