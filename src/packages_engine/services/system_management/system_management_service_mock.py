from dataclasses import dataclass
from typing import Callable, Optional

from packages_engine.models.operation_result import OperationResult

from .system_management_service_contract import SystemManagementServiceContract

@dataclass
class ExecuteCommandParams:
    command: list[str]
    directory: Optional[str] = None

class MockSystemManagementService(SystemManagementServiceContract):
    def __init__(self):
        self.is_installed_params: list[str] = []
        self.is_installed_result = True
        self.install_params: list[str] = []
        self.install_result = OperationResult[bool].succeed(True)
        self.is_running_params: list[str] = []
        self.is_running_result = OperationResult[bool].succeed(True)
        self.start_params: list[str] = []
        self.start_result = OperationResult[bool].succeed(True)
        self.restart_params: list[str] = []
        self.restart_result = OperationResult[bool].succeed(True)
        self.execute_command_params: list[ExecuteCommandParams] = []
        self.execute_command_result = OperationResult[bool].succeed(True)
        self.execute_raw_command_params: list[str] = []
        self.execute_raw_command_result = OperationResult[bool].succeed(True)
        self.execute_raw_command_result_fn: Optional[Callable[[str], OperationResult[bool]]] = None

    def is_installed(self, package: str) -> bool:
        self.is_installed_params.append(package)
        return self.is_installed_result
    
    def install(self, package: str) -> OperationResult[bool]:
        self.install_params.append(package)
        return self.install_result

    def is_running(self, package: str) -> OperationResult[bool]:
        self.is_running_params.append(package)
        return self.is_running_result
    
    def start(self, package: str) -> OperationResult[bool]:
        self.start_params.append(package)
        return self.start_result
    
    def restart(self, package: str) -> OperationResult[bool]:
        self.restart_params.append(package)
        return self.restart_result
    
    def execute_command(self, command: list[str], directory: Optional[str] = None) -> OperationResult[bool]:
        self.execute_command_params.append(ExecuteCommandParams(command, directory))
        return self.execute_command_result
    
    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        self.execute_raw_command_params.append(command)
        if self.execute_raw_command_result_fn != None:
            return self.execute_raw_command_result_fn(command)
        return self.execute_raw_command_result