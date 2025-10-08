"""Mock System Management Service - test double for low-level system operations."""

from dataclasses import dataclass
from typing import Callable, Optional

from packages_engine.models.operation_result import OperationResult

from .system_management_service_contract import SystemManagementServiceContract


@dataclass
class ExecuteCommandParams:
    """
    Data class storing parameters from an execute_command call.

    Attributes:
        command: The command arguments list.
        directory: The optional working directory.
    """

    command: list[str]
    directory: Optional[str] = None


class MockSystemManagementService(SystemManagementServiceContract):
    """
    Mock implementation of SystemManagementService for testing purposes.

    Tracks all system management operations and their parameters, allowing tests
    to verify correct usage. Supports configurable return values for all operations
    and callable result functions for dynamic behavior.

    Attributes:
        is_installed_params: List of package names from is_installed calls.
        is_installed_result: Default result for is_installed calls.
        install_params: List of package names from install calls.
        install_result: Default result for install calls.
        is_running_params: List of package names from is_running calls.
        is_running_result: Default result for is_running calls.
        start_params: List of package names from start calls.
        start_result: Default result for start calls.
        restart_params: List of package names from restart calls.
        restart_result: Default result for restart calls.
        execute_command_params: List of ExecuteCommandParams from execute_command calls.
        execute_command_result: Default result for execute_command calls.
        execute_raw_command_params: List of command strings from execute_raw_command calls.
        execute_raw_command_result: Default result for execute_raw_command calls.
        execute_raw_command_result_fn: Optional callable for dynamic execute_raw_command results.
    """

    def __init__(self):
        """Initialize the mock service with empty tracking lists and default success values."""
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
        """
        Record an is_installed call and return configured result.

        Args:
            package: The package name to record.

        Returns:
            The configured is_installed_result value.
        """
        self.is_installed_params.append(package)
        return self.is_installed_result

    def install(self, package: str) -> OperationResult[bool]:
        """
        Record an install call and return configured result.

        Args:
            package: The package name to record.

        Returns:
            The configured install_result value.
        """
        self.install_params.append(package)
        return self.install_result

    def is_running(self, package: str) -> OperationResult[bool]:
        """
        Record an is_running call and return configured result.

        Args:
            package: The package name to record.

        Returns:
            The configured is_running_result value.
        """
        self.is_running_params.append(package)
        return self.is_running_result

    def start(self, package: str) -> OperationResult[bool]:
        """
        Record a start call and return configured result.

        Args:
            package: The package name to record.

        Returns:
            The configured start_result value.
        """
        self.start_params.append(package)
        return self.start_result

    def restart(self, package: str) -> OperationResult[bool]:
        """
        Record a restart call and return configured result.

        Args:
            package: The package name to record.

        Returns:
            The configured restart_result value.
        """
        self.restart_params.append(package)
        return self.restart_result

    def execute_command(
        self, command: list[str], directory: Optional[str] = None
    ) -> OperationResult[bool]:
        """
        Record an execute_command call and return configured result.

        Args:
            command: The command arguments to record.
            directory: The optional working directory to record.

        Returns:
            The configured execute_command_result value.
        """
        self.execute_command_params.append(ExecuteCommandParams(command, directory))
        return self.execute_command_result

    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        """
        Record an execute_raw_command call and return configured result.

        If execute_raw_command_result_fn is set, calls it with the command and
        returns its result. Otherwise returns the configured execute_raw_command_result.

        Args:
            command: The command string to record.

        Returns:
            Result from result_fn if set, otherwise default execute_raw_command_result.
        """
        self.execute_raw_command_params.append(command)
        if self.execute_raw_command_result_fn is not None:
            return self.execute_raw_command_result_fn(command)
        return self.execute_raw_command_result
