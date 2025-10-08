"""Linux Ubuntu Engine Service - Ubuntu-specific system management implementation."""

import subprocess
import sys
from typing import Optional

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.system_management_engine.system_management_engine_service import (
    SystemManagementEngineService,
)


class LinuxUbuntuEngineService(SystemManagementEngineService):
    """
    Ubuntu Linux-specific implementation of system management engine.

    Provides system-level operations for Ubuntu Linux using dpkg for package queries,
    apt-get for package installation, and systemctl for service management.
    All operations are executed using subprocess with appropriate permissions.
    """

    def is_installed(self, package: str) -> bool:
        """
        Check if a package is installed using dpkg.

        Args:
            package: The name of the package to check.

        Returns:
            True if the package is installed, False otherwise.
        """
        try:
            subprocess.run(
                ["dpkg", "-s", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def install(self, package: str) -> OperationResult[bool]:
        """
        Install a package using apt-get with automatic update.

        Runs 'apt-get update' followed by 'apt-get install -y' to install
        the specified package with automatic yes to prompts.

        Args:
            package: The name of the package to install.

        Returns:
            OperationResult indicating success or failure with error details.
        """
        try:
            subprocess.run(
                ["sudo", "apt-get", "update"], stdout=sys.stdout, stderr=sys.stderr, check=True
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True,
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(
                f"Failed to install '{package}'. Code: {e.returncode}.", e.returncode
            )

    def is_running(self, package: str) -> OperationResult[bool]:
        """
        Check if a service is running using systemctl.

        Uses 'systemctl is-active' to check service status. Handles return codes:
        - 'active': Service is running (returns True)
        - 'inactive' or 'failed': Service is not running (returns False)
        - returncode 3: Service unit not found (returns False)

        Args:
            package: The name of the service to check.

        Returns:
            OperationResult containing True if running, False if not, or failure details.
        """
        try:
            is_active_result = subprocess.run(
                ["systemctl", "is-active", package], capture_output=True, text=True, check=True
            ).stdout.strip()

            if is_active_result == "active":
                return OperationResult[bool].succeed(True)
            elif is_active_result == "inactive" or is_active_result == "failed":
                return OperationResult[bool].succeed(False)

            return OperationResult[bool].fail(
                f"Failed to check running status for the '{package}' due to unknown result returned. Result: '{is_active_result}'",
                0,
            )
        except subprocess.CalledProcessError as e:
            if e.returncode == 3:
                return OperationResult[bool].succeed(False)
            return OperationResult[bool].fail(
                f"Failed to check running status for the '{package}'. Code: {e.returncode}.",
                e.returncode,
            )

    def start(self, package: str) -> OperationResult[bool]:
        """
        Start a service using systemctl.

        Args:
            package: The name of the service to start.

        Returns:
            OperationResult indicating success or failure with error details.
        """
        try:
            subprocess.run(
                ["systemctl", "start", package], stdout=sys.stdout, stderr=sys.stderr, check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(
                f"Failed to start '{package}'. Code: {e.returncode}.", e.returncode
            )

    def restart(self, package: str) -> OperationResult[bool]:
        """
        Restart a service using systemctl reload.

        Uses 'systemctl reload' to reload the service configuration without
        a full restart.

        Args:
            package: The name of the service to restart.

        Returns:
            OperationResult indicating success or failure with error details.
        """
        try:
            subprocess.run(
                ["systemctl", "reload", package], stdout=sys.stdout, stderr=sys.stderr, check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(
                f"Failed to restart '{package}'. Code: {e.returncode}.", e.returncode
            )

    def execute_command(
        self, command: list[str], directory: Optional[str] = None
    ) -> OperationResult[bool]:
        """
        Execute a command with optional working directory.

        Runs the command as a subprocess with the specified working directory
        if provided.

        Args:
            command: The command to execute as a list of arguments.
            directory: Optional working directory for command execution.

        Returns:
            OperationResult indicating success or failure with error details.
        """
        try:
            subprocess.run(command, cwd=directory, stdout=sys.stdout, stderr=sys.stderr, check=True)

            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(
                f"Command failed. Code: {e.returncode}.", e.returncode
            )

    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        """
        Execute a raw shell command string using bash.

        Runs the command through 'bash -lc' to execute as a login shell,
        enabling access to user environment and aliases.

        Args:
            command: The raw shell command string to execute.

        Returns:
            OperationResult indicating success or failure with error details.
        """
        shell_exe = ["bash", "-lc", command]
        try:
            subprocess.run(shell_exe, stdout=sys.stdout, stderr=sys.stderr, check=True)
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(
                f"Command failed. Code: {e.returncode}.", e.returncode
            )
