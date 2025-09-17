from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models.operation_result import OperationResult

class SystemManagementEngineService(ABC):
    @abstractmethod
    def is_installed(self, package: str) -> bool:
        pass

    @abstractmethod
    def install(self, package: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def is_running(self, package: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def start(self, package: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def restart(self, package: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def execute_command(self, command: list[str], directory: Optional[str] = None) -> OperationResult[bool]:
        pass

    @abstractmethod
    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        pass