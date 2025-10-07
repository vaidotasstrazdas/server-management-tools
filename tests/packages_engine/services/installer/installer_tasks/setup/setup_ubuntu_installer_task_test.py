"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.setup import SetupUbuntuInstallerTask
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestSetupUbuntuInstallerTask(unittest.TestCase):
    """Setup Ubuntu Installer Task Tests"""

    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: SetupUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = SetupUbuntuInstallerTask(self.notifications, self.controller)

    def test_notifications_flow_on_success(self):
        """Notifications flow on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {
                    "type": "info",
                    "text": "Installation setup task will be executed before installing other dependencies",
                },
            ],
        )

    def test_notifications_flow_on_failure(self):
        """Notifications flow on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {
                    "type": "info",
                    "text": "Installation setup task will be executed before installing other dependencies",
                },
                {"type": "error", "text": "Command failed. Message: failure."},
            ],
        )

    def test_correct_commands_executed(self):
        """Correct commands executed."""
        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(
            params,
            [
                [
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get update",
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl gnupg lsb-release",
                ]
            ],
        )

    def test_returns_result_from_packages_controller_on_success(self):
        """Returns result from packages controller on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_result_from_packages_controller_on_failure(self):
        """Returns result from packages controller on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)
