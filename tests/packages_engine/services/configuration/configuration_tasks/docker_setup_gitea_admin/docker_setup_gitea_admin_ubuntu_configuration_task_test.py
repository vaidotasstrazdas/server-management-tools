"""Tests for DockerSetupGiteaAdminUbuntuConfigurationTask.

This module contains unit tests for the Gitea administrator setup configuration
task on Ubuntu systems, verifying the correct behavior of admin user creation
and error handling.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_tasks.docker_setup_gitea_admin import (
    DockerSetupGiteaAdminUbuntuConfigurationTask,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestDockerSetupGiteaAdminUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for DockerSetupGiteaAdminUbuntuConfigurationTask.

    Tests verify that the configuration task correctly:
    - Creates Gitea admin users with provided credentials
    - Executes proper Docker commands
    - Handles command failures appropriately
    - Produces correct notification flows
    """

    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DockerSetupGiteaAdminUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DockerSetupGiteaAdminUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.gitea_admin_login = "admin"
        self.data.gitea_admin_email = "admin@example.com"
        self.data.gitea_admin_password = "123456"

        self.reader.read_result = OperationResult[str].succeed("gitea-config-content")

    def test_happy_path(self):
        """Test successful Gitea admin setup returns success result."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        """Test successful setup produces expected info and success notifications."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Setting up Gitea Administrator User.", "type": "info"},
                {"text": "\tGitea admin present.", "type": "success"},
            ],
        )

    def test_runs_correct_commands(self):
        """Test that correct Docker commands are executed with proper credentials."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    "sudo bash -lc 'if ! docker exec gitea gitea admin user list --admin "
                    "2>/dev/null | grep -qw admin; then   docker exec gitea gitea admin user "
                    "create --admin --username admin --password 123456 --email admin@example.com "
                    "--must-change-password=false; fi'"
                ]
            ],
        )

    def test_command_failure_results_in_operation_failure(self):
        """Test that command execution failure results in operation failure."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_command_failure_results_in_operation_failure_notifications_flow(
        self,
    ):
        """Test that command failure produces expected error notification flow."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Setting up Gitea Administrator User.", "type": "info"},
                {"text": "\tEnsuring Gitea admin failed.", "type": "error"},
            ],
        )
