from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models import OperationResult

class PackageControllerServiceContract(ABC):
    @abstractmethod
    def install_package(self, package: str):
        pass

    @abstractmethod
    def ensure_running(self, package: str):
        pass

    @abstractmethod
    def run_command(self, command: list[str], directory: Optional[str] = None):
        pass

    @abstractmethod
    def run_raw_command(self, command: str):
        pass

    @abstractmethod
    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        pass