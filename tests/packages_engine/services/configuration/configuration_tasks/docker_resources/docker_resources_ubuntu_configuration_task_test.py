"""Tests for DockerResourcesUbuntuConfigurationTask. Validates Docker compose file and directory setup on Ubuntu."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.docker_resources import (
    DockerResourcesUbuntuConfigurationTask,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
    WriteTextParams,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestDockerResourcesUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for DockerResourcesUbuntuConfigurationTask. Verifies compose template reading, directory creation, and permissions."""
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DockerResourcesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DockerResourcesUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"

        self.file_system.write_text_result_map = {
            "/srv/stack/docker-compose.yml": OperationResult[bool].succeed(True),
        }

        self.reader.read_result = OperationResult[str].succeed("docker-compose-content")
        self.maxDiff = None

    def test_happy_path(self):
        """Verifies successful configuration returns success result."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        """Verifies correct notification messages are sent during successful resource setup."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Creating Docker folders if they do not exist.", "type": "info"},
                {"text": "Creating Docker folders successful.", "type": "success"},
                {"text": "Reading Docker Config template data.", "type": "info"},
                {"text": "\tReading Docker Config template data succeeded.", "type": "success"},
                {"text": "Writing Docker configuration.", "type": "info"},
                {"text": "\tWriting Docker configuration succeeded.", "type": "success"},
                {"text": "Fixing Docker configuration permissions.", "type": "info"},
                {"text": "Fixing Docker configuration permissions successful.", "type": "success"},
            ],
        )

    def test_runs_correct_configuration_commands(self):
        """Verifies correct directory creation and permission commands are executed."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    "sudo install -d -m 0755 /srv/stack",
                    "sudo install -d -m 0700 -o 999 -g 999 /srv/postgres/data",
                    "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/data",
                    "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config",
                    "sudo install -d -m 0750 -o 5050 -g 5050 /srv/pgadmin/data",
                ],
                [
                    "sudo chown root:root /srv/stack/docker-compose.yml",
                    "sudo chmod 0644 /srv/stack/docker-compose.yml",
                ],
            ],
        )

    def test_failure_to_setup_dirs_results_in_failure(self):
        """Verifies directory creation failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo install -d -m 0755 /srv/stack"] = (
            failure_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_setup_dirs_results_in_failure_notifications_flow(self):
        """Verifies error notifications are sent when directory creation fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo install -d -m 0755 /srv/stack"] = (
            failure_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Creating Docker folders if they do not exist.", "type": "info"},
                {"text": "Failed creating Docker folders.", "type": "error"},
            ],
        )

    def test_failure_to_setup_permissions_results_in_failure(self):
        """Verifies permission setup failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo chown root:root"] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_setup_permissions_results_in_failure_notifications_flow(self):
        """Verifies error notifications are sent when permission setup fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo chown root:root"] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Creating Docker folders if they do not exist.", "type": "info"},
                {"text": "Creating Docker folders successful.", "type": "success"},
                {"text": "Reading Docker Config template data.", "type": "info"},
                {"text": "\tReading Docker Config template data succeeded.", "type": "success"},
                {"text": "Writing Docker configuration.", "type": "info"},
                {"text": "\tWriting Docker configuration succeeded.", "type": "success"},
                {"text": "Fixing Docker configuration permissions.", "type": "info"},
                {"text": "Fixing Docker configuration permissions failed.", "type": "error"},
            ],
        )

    def test_reads_docker_configuration_template_correctly(self):
        """Verifies docker-compose template is read from correct path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/docker-compose.yml",
                )
            ],
        )

    def test_docker_config_template_read_failure_results_in_command_failure(self):
        """Verifies template read failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_docker_config_template_read_failure_results_in_command_failure_notifications_flow(
        self,
    ):
        """Verifies error notifications are sent when template read fails."""
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Creating Docker folders if they do not exist.", "type": "info"},
                {"text": "Creating Docker folders successful.", "type": "success"},
                {"text": "Reading Docker Config template data.", "type": "info"},
                {"text": "\tReading Docker Config template data failed.", "type": "error"},
            ],
        )

    def test_docker_config_is_stored_on_server(self):
        """Verifies docker-compose.yml is written to correct server path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/srv/stack/docker-compose.yml", "docker-compose-content")],
        )

    def test_failure_to_store_config_on_server_result_in_failure(self):
        """Verifies file write failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/srv/stack/docker-compose.yml"] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_config_on_server_result_in_failure_notifications_flow(self):
        """Verifies error notifications are sent when file write fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/srv/stack/docker-compose.yml"] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Creating Docker folders if they do not exist.", "type": "info"},
                {"text": "Creating Docker folders successful.", "type": "success"},
                {"text": "Reading Docker Config template data.", "type": "info"},
                {"text": "\tReading Docker Config template data succeeded.", "type": "success"},
                {"text": "Writing Docker configuration.", "type": "info"},
                {"text": "\tWriting Docker configuration failed.", "type": "error"},
            ],
        )
