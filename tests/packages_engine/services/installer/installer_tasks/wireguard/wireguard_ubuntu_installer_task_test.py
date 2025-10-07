"""Imports necessary for the tests to run."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.wireguard import (
    WireguardUbuntuInstallerTask,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)
from packages_engine.services.system_management_engine.system_management_engine_service_mock import (
    MockSystemManagementEngineService,
)


class TestWireguardUbuntuInstallerTask(unittest.TestCase):
    """Tests of Wireguard installer task on Linux Ubuntu Server platform."""

    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: WireguardUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = WireguardUbuntuInstallerTask(self.notifications, self.engine, self.controller)

    def test_checks_for_wireguard_installation_status(self):
        """Checks for Wireguard installation status"""
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ["wireguard", "wireguard-tools"])

    def test_notification_flow_when_wireguard_installed_already(self):
        """Notification flow when Wireguard installed already"""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "WireGuard will be installed now if it is not installed."},
                {
                    "type": "success",
                    "text": "\tWireGuard is installed already. Nothing needs to be done.",
                },
            ],
        )

    def test_notification_flow_when_wireguard_not_installed(self):
        """Notifications flow when Wireguard not installed."""
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [{"type": "info", "text": "WireGuard will be installed now if it is not installed."}],
        )

    def test_notification_flow_when_wireguard_not_installed_and_commands_fail(self):
        """Notifications flow when Wireguard not installed and commands fail."""
        # Arrange
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = OperationResult[bool].fail("failure")

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "WireGuard will be installed now if it is not installed."},
                {"type": "error", "text": "Command failed. Message: failure."},
            ],
        )

    def test_no_commands_executed_when_wireguard_installed_already(self):
        """No commands executed when Wireguard installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_wireguard_not_installed(self):
        """Correct commands executed when Wireguard not installed."""
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(
            params,
            [
                [
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "
                    "wireguard wireguard-tools",
                    "sudo install -d -m 0700 -o root -g root /etc/wireguard /etc/wireguard/clients",
                ]
            ],
        )

    def test_returns_result_from_packages_controller_when_wireguard_not_installed(self):
        """Returns result from packages controller when Wireguard not installed."""
        # Arrange
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = OperationResult[bool].succeed(True)

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_fail_result_from_packages_controller_when_wireguard_not_installed_on_command_failure(
        self,
    ):
        """Returns fail result from packages controller when Wireguard not installed on command failure."""
        # Arrange
        fail_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, fail_result)

    def test_returns_success_result_when_wireguard_installed(self):
        """Returns success result when Wireguard installed."""
        # Arrange
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = OperationResult[bool].fail("failure")

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))
