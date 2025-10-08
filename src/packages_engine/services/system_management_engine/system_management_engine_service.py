"""System Management Engine Service - abstract base for platform-specific system management."""

from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models.operation_result import OperationResult


class SystemManagementEngineService(ABC):
    """
    Abstract base class for platform-specific system management engines.

    Defines the interface that must be implemented by concrete platform engines
    (e.g., LinuxUbuntuEngineService) to provide system-level operations for that platform.
    """

    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """
        Check if a package is installed on the system.

        Args:
            package: The name of the package to check.

        Returns:
            True if the package is installed, False otherwise.
        """

    @abstractmethod
    def install(self, package: str) -> OperationResult[bool]:
        """
        Install a package on the system.

        Args:
            package: The name of the package to install.

        Returns:
            OperationResult indicating success or failure of the installation.
        """

    @abstractmethod
    def is_running(self, package: str) -> OperationResult[bool]:
        """
        Check if a service/package is currently running.

        Args:
            package: The name of the service/package to check.

        Returns:
            OperationResult containing True if running, False if not, or failure details.
        """

    @abstractmethod
    def start(self, package: str) -> OperationResult[bool]:
        """
        Start a service/package.

        Args:
            package: The name of the service/package to start.

        Returns:
            OperationResult indicating success or failure of the start operation.
        """

    @abstractmethod
    def restart(self, package: str) -> OperationResult[bool]:
        """
        Restart a service/package.

        Args:
            package: The name of the service/package to restart.

        Returns:
            OperationResult indicating success or failure of the restart operation.
        """

    @abstractmethod
    def execute_command(
        self, command: list[str], directory: Optional[str] = None
    ) -> OperationResult[bool]:
        """
        Execute a command with optional working directory.

        Args:
            command: The command to execute as a list of arguments.
            directory: Optional working directory for command execution.

        Returns:
            OperationResult indicating success or failure of the command execution.
        """

    @abstractmethod
    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        """
        Execute a raw shell command string.

        Args:
            command: The raw shell command string to execute.

        Returns:
            OperationResult indicating success or failure of the command execution.
        """
