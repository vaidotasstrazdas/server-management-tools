"""Package Controller Service Contract - defines interface for package management operations."""

from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models import OperationResult


class PackageControllerServiceContract(ABC):
    """
    Abstract base class defining the contract for package controller services.

    Provides methods to install packages, ensure services are running, and execute
    system commands with user feedback through notifications.
    """

    @abstractmethod
    def install_package(self, package: str):
        """
        Install a package if it is not already installed.

        Args:
            package: The name of the package to install.
        """

    @abstractmethod
    def ensure_running(self, package: str):
        """
        Ensure a package/service is running, starting or restarting it as needed.

        Args:
            package: The name of the package/service to ensure is running.
        """

    @abstractmethod
    def run_command(self, command: list[str], directory: Optional[str] = None):
        """
        Execute a command with optional working directory.

        Args:
            command: The command to execute as a list of arguments.
            directory: Optional working directory for command execution.
        """

    @abstractmethod
    def run_raw_command(self, command: str):
        """
        Execute a raw shell command string.

        Args:
            command: The raw shell command string to execute.
        """

    @abstractmethod
    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        """
        Execute multiple raw shell commands sequentially.

        Args:
            commands: List of raw shell command strings to execute.

        Returns:
            OperationResult indicating success if all commands succeed, or failure
            with details about the first failed command.
        """
