from dataclasses import dataclass
from typing import Optional

from packages_engine.models import OperationResult

from .package_controller_service_contract import PackageControllerServiceContract

@dataclass
class RunCommandParams:
    command: list[str]
    directory: Optional[str] = None

class MockPackageControllerService(PackageControllerServiceContract):
    def __init__(self):
        self.install_package_params: list[str] = []
        self.ensure_running_params: list[str] = []
        self.run_command_params: list[RunCommandParams] = []
        self.run_raw_command_params: list[str] = []
        self.run_raw_commands_params: list[list[str]] = []
        self.run_raw_commands_result = OperationResult[bool].succeed(True)

    def install_package(self, package: str):
        self.install_package_params.append(package)
    
    def ensure_running(self, package: str):
        self.ensure_running_params.append(package)

    def run_command(self, command: list[str], directory: Optional[str] = None):
        self.run_command_params.append(RunCommandParams(command, directory))

    def run_raw_command(self, command: str):
        self.run_raw_command_params.append(command)

    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        self.run_raw_commands_params.append(commands)
        return self.run_raw_commands_result