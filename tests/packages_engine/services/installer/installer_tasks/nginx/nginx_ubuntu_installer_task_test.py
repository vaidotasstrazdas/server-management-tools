"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.nginx import NginxUbuntuInstallerTask
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)
from packages_engine.services.system_management_engine.system_management_engine_service_mock import (
    MockSystemManagementEngineService,
)


class TestNginxUbuntuInstallerTask(unittest.TestCase):
    """Nginx Ubuntu Installer Task Tests"""

    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: NginxUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = NginxUbuntuInstallerTask(self.notifications, self.engine, self.controller)

    def test_checks_for_nginx_installation_status(self):
        """Checks for Nginx installation status."""
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ["nginx"])

    def test_notifications_flow_when_nginx_installed_already(self):
        """Notifications flow when Nginx installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "Nginx will be installed now if it is not installed."},
                {
                    "type": "success",
                    "text": "\tNginx is installed already. Nothing needs to be done.",
                },
            ],
        )

    def test_notifications_flow_when_nginx_not_installed_on_success(self):
        """Notifications flow when Nginx not installed on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [{"type": "info", "text": "Nginx will be installed now if it is not installed."}],
        )

    def test_notifications_flow_when_nginx_not_installed_on_failure(self):
        """Notifications flow when Nginx not installed on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "Nginx will be installed now if it is not installed."},
                {"type": "error", "text": "Command failed. Message: failure."},
            ],
        )

    def test_no_commands_executed_when_nginx_installed_already(self):
        """No commands executed when Nginx installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_nginx_not_installed(self):
        """Correct commands executed when Nginx not installed."""
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
                    # Install nginx + stream module, lean install
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install "
                    "-y --no-install-recommends nginx libnginx-mod-stream",
                    # Remove only the default-enabled site (symlink). Keep sites-available intact.
                    "sudo rm -f /etc/nginx/sites-enabled/default",
                    # Keep Nginx stopped until the config task writes proper configs and validates them.
                    # This keeps ports 80/443 closed from nginx side (your firewall may still block).
                    "sudo systemctl disable --now nginx || true",
                ]
            ],
        )

    def test_returns_result_from_packages_controller_when_nginx_not_installed_on_success(self):
        """Returns result from packages controller when Nginx not installed on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_result_from_packages_controller_when_nginx_not_installed_on_failure(self):
        """Returns result from packages controller when Nginx not installed on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_nginx_installed(self):
        """Returns success result when Nginx installed even if the command would fail."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))
