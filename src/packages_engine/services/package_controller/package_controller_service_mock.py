from dataclasses import dataclass
from typing import Optional, Dict

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
        self.run_raw_commands_result_regex_map: Dict[str, OperationResult[bool]] = {}

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

        for command in commands:
            print(command)
            result_found = self._find_result(command)
            if result_found != None:
                return result_found

        return self.run_raw_commands_result
    
    def _find_result(self, command: str) -> OperationResult[bool] | None:
        for key in self.run_raw_commands_result_regex_map.keys():
            if command in key:
                return self.run_raw_commands_result_regex_map[key]
        return None