"""Mock Package Controller Service - test double for package management operations."""

from dataclasses import dataclass
from typing import Dict, Optional

from packages_engine.models import OperationResult

from .package_controller_service_contract import PackageControllerServiceContract


@dataclass
class RunCommandParams:
    """
    Data class storing parameters from a run_command call.

    Attributes:
        command: The command arguments list.
        directory: The optional working directory.
    """

    command: list[str]
    directory: Optional[str] = None


class MockPackageControllerService(PackageControllerServiceContract):
    """
    Mock implementation of PackageControllerService for testing purposes.

    Tracks all package management operations and their parameters, allowing tests
    to verify correct usage. Supports configurable return values and regex-based
    result mapping for complex test scenarios.

    Attributes:
        install_package_params: List of package names from install_package calls.
        ensure_running_params: List of package names from ensure_running calls.
        run_command_params: List of RunCommandParams from run_command calls.
        run_raw_command_params: List of command strings from run_raw_command calls.
        run_raw_commands_params: List of command lists from run_raw_commands calls.
        run_raw_commands_result: Default result for run_raw_commands.
        run_raw_commands_result_regex_map: Map of command patterns to specific results.
    """

    def __init__(self):
        """Initialize the mock service with empty tracking lists and default values."""
        self.install_package_params: list[str] = []
        self.ensure_running_params: list[str] = []
        self.run_command_params: list[RunCommandParams] = []
        self.run_raw_command_params: list[str] = []
        self.run_raw_commands_params: list[list[str]] = []
        self.run_raw_commands_result = OperationResult[bool].succeed(True)
        self.run_raw_commands_result_regex_map: Dict[str, OperationResult[bool]] = {}

    def install_package(self, package: str):
        """
        Record an install_package call.

        Args:
            package: The package name to record.
        """
        self.install_package_params.append(package)

    def ensure_running(self, package: str):
        """
        Record an ensure_running call.

        Args:
            package: The package name to record.
        """
        self.ensure_running_params.append(package)

    def run_command(self, command: list[str], directory: Optional[str] = None):
        """
        Record a run_command call.

        Args:
            command: The command arguments to record.
            directory: The optional working directory to record.
        """
        self.run_command_params.append(RunCommandParams(command, directory))

    def run_raw_command(self, command: str):
        """
        Record a run_raw_command call.

        Args:
            command: The command string to record.
        """
        self.run_raw_command_params.append(command)

    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        """
        Record a run_raw_commands call and return configured result.

        Checks regex map for matching command patterns and returns the
        corresponding result, otherwise returns the default result.

        Args:
            commands: The command list to record.

        Returns:
            Result from regex map if command matches, otherwise default result.
        """
        self.run_raw_commands_params.append(commands)

        for command in commands:
            result_found = self._find_result(command)
            if result_found is not None:
                return result_found

        return self.run_raw_commands_result

    def _find_result(self, command: str) -> OperationResult[bool] | None:
        """
        Find a configured result for a command pattern.

        Args:
            command: The command to match against patterns.

        Returns:
            Matching result if found, None otherwise.
        """
        for item in self.run_raw_commands_result_regex_map.items():
            if command in item[0]:
                return self.run_raw_commands_result_regex_map[item[0]]
        return None
