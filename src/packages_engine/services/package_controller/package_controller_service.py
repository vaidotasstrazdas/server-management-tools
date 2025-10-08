"""Package Controller Service - high-level package management with user notifications."""

from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.system_management import SystemManagementServiceContract

from .package_controller_service_contract import PackageControllerServiceContract


class PackageControllerService(PackageControllerServiceContract):
    """
    High-level package management service providing user feedback through notifications.

    Wraps low-level system management operations with user-friendly notification messages
    about installation progress, service status, and command execution results.

    Attributes:
        system_management_service: Low-level system management operations.
        notifications_service: User notification service for feedback messages.
    """
    system_management_service: SystemManagementServiceContract
    notifications_service: NotificationsServiceContract

    def __init__(
        self,
        system_management_service: SystemManagementServiceContract,
        notifications_service: NotificationsServiceContract,
    ):
        """
        Initialize the package controller service.

        Args:
            system_management_service: Service for low-level system operations.
            notifications_service: Service for user notifications and feedback.
        """
        self.system_management_service = system_management_service
        self.notifications_service = notifications_service

    def install_package(self, package: str):
        """
        Install a package if not already installed, with progress notifications.

        Checks if the package is installed and attempts installation if needed,
        providing user feedback at each step through notifications.

        Args:
            package: The name of the package to install.
        """
        self.notifications_service.info(f'Will try to install "{package}" if it is not installed.')
        self.notifications_service.info(f'Checking if "{package}" is installed.')
        is_installed = self.system_management_service.is_installed(package)
        if not is_installed:
            self.notifications_service.info(
                f'Package "{package}" is not installed. Will try installing it now.'
            )
            install_result = self.system_management_service.install(package)
            if install_result.success:
                self.notifications_service.success(
                    f'Package "{package}" was installed successfully.'
                )
            else:
                self.notifications_service.error(
                    f'Failed to install the "{package}". Error code: {install_result.code}. Error message: "{install_result.message}".'
                )
        else:
            self.notifications_service.success(
                f'Package "{package}" is installed already, nothing needs to be done.'
            )

    def ensure_running(self, package: str):
        """
        Ensure a service/package is running, starting or restarting as needed.

        Checks the running status, starts the service if stopped, and performs
        a restart. Provides detailed user feedback through notifications at each step.

        Args:
            package: The name of the service/package to ensure is running.
        """
        self.notifications_service.info(
            f'Will try ensuring that package "{package}" is up and running.'
        )
        self.notifications_service.info(f'Checking if the package "{package}" is running already.')
        is_running_result = self.system_management_service.is_running(package)
        if is_running_result.success:
            self.notifications_service.success(
                f'Running state check for the package "{package}" succeeded.'
            )
            is_running = is_running_result.data
            if is_running:
                self.notifications_service.info(f'Package "{package}" is running. Will restart it.')
            else:
                self.notifications_service.info(
                    f'Package "{package}" is not running. Will start it first.'
                )

                start_result = self.system_management_service.start(package)
                if start_result.success:
                    self.notifications_service.success(
                        f'Package "{package}" has been started successfully.'
                    )
                else:
                    self.notifications_service.error(
                        f'Failed to start package "{package}". Error Code: {start_result.code}. Error Message: "{start_result.message}".'
                    )
                    return

            restart_result = self.system_management_service.restart(package)
            if restart_result.success:
                self.notifications_service.success(
                    f'Package "{package}" has been restarted successfully.'
                )
            else:
                self.notifications_service.error(
                    f'Failed to restart package "{package}". Error Code: {restart_result.code}. Error Message: "{restart_result.message}".'
                )
        else:
            self.notifications_service.error(
                f'Check failed for the package "{package}". Error Code: {is_running_result.code}. Error Message: "{is_running_result.message}".'
            )

    def run_command(self, command: list[str], directory: Optional[str] = None):
        """
        Execute a command with optional working directory and user notifications.

        Runs the command and provides feedback about the execution directory
        and success/failure status through notifications.

        Args:
            command: The command to execute as a list of arguments.
            directory: Optional working directory for command execution.
        """
        command_str = str.join(" ", command)
        self.notifications_service.info(f'Running command: "{command_str}".')
        if directory is not None:
            self.notifications_service.info(f'Command directory selected: "{directory}".')

        result = self.system_management_service.execute_command(command, directory)
        if result.success:
            self.notifications_service.success("Running command succeeded!")
        else:
            self.notifications_service.error(
                f'Running command failed. Error Code: {result.code}. Error Message: "{result.message}".'
            )

    def run_raw_command(self, command: str):
        """
        Execute a raw shell command string with user notifications.

        Runs the raw command and provides feedback about success or failure
        through notifications.

        Args:
            command: The raw shell command string to execute.
        """
        self.notifications_service.info(f'Running command in raw mode: "{command}".')
        result = self.system_management_service.execute_raw_command(command)
        if result.success:
            self.notifications_service.success("Running command succeeded!")
        else:
            self.notifications_service.error(
                f'Running command failed. Error Code: {result.code}. Error Message: "{result.message}".'
            )

    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        """
        Execute multiple raw shell commands sequentially with per-command notifications.

        Runs each command in sequence, stopping at the first failure. Provides
        individual feedback for each command execution through notifications.

        Args:
            commands: List of raw shell command strings to execute.

        Returns:
            OperationResult indicating success if all commands succeed, or failure
            with details about the first failed command.
        """
        for command in commands:
            self.notifications_service.info(f'Will execute command: "{command}"')
            execute_raw_command_result = self.system_management_service.execute_raw_command(command)
            if not execute_raw_command_result.success:
                self.notifications_service.error("\tCommand execution failed.")
                return OperationResult[bool].fail(f'Failed on "{command}"')
            else:
                self.notifications_service.success("\tCommand execution successful.")
        return OperationResult[bool].succeed(True)
