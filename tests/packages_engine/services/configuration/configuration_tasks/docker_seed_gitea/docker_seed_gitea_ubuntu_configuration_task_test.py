"""Tests for DockerSeedGiteaUbuntuConfigurationTask.

Verifies Gitea app.ini configuration seeding on Ubuntu systems.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.docker_seed_gitea import (
    DockerSeedGiteaUbuntuConfigurationTask,
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


class TestDockerSeedGiteaUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for DockerSeedGiteaUbuntuConfigurationTask.

    Tests Gitea config seeding including template reading, file writing,
    directory creation, and permission setup.
    """
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DockerSeedGiteaUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DockerSeedGiteaUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"

        self.file_system.write_text_result_map = {
            "/srv/gitea/config/app.ini": OperationResult[bool].succeed(True),
        }

        self.file_system.path_exists_result_map = {"/srv/gitea/config/app.ini": False}

        self.reader.read_result = OperationResult[str].succeed("gitea-config-content")
        self.maxDiff = None

    def test_happy_path(self):
        """Verifies successful Gitea seeding returns success result."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        """Verifies correct notification messages during successful seeding."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {"text": "Will read Gitea configurations template.", "type": "info"},
                {"text": "\tReading Gitea configurations template succeeded.", "type": "success"},
                {"text": "Will install Gitea path if it does not exist.", "type": "info"},
                {"text": "\tInstall succeeded.", "type": "success"},
                {"text": "Gitea configuration does not exist. Will create it now.", "type": "info"},
                {"text": "\tSucceeded in saving Gitea configuration.", "type": "success"},
                {"text": "Will process Gitea permissions.", "type": "info"},
                {"text": "\tProcessing succeeded.", "type": "success"},
            ],
        )

    def test_runs_correct_commands_when_path_does_not_exist(self):
        """Verifies directory creation and permission commands are executed."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                ["umask 0137 && install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config"],
                [
                    "sudo chown 1000:1000 /srv/gitea/config/app.ini && sudo chmod 0640 "
                    "/srv/gitea/config/app.ini"
                ],
            ],
        )

    def test_runs_no_commands_when_path_exists(self):
        """Verifies no commands run when config already exists."""
        # Arrange
        self.file_system.path_exists_result_map = {"/srv/gitea/config/app.ini": True}

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [],
        )

    def test_happy_path_when_config_path_exists(self):
        """Verifies success when config file already exists."""
        # Arrange
        self.file_system.path_exists_result_map = {"/srv/gitea/config/app.ini": True}

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow_when_config_path_exists(self):
        """Verifies correct notifications when config already exists."""
        # Arrange
        self.file_system.path_exists_result_map = {"/srv/gitea/config/app.ini": True}

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {
                    "text": "\tGitea configuration exists already. Nothing needs to be done.",
                    "type": "success",
                },
            ],
        )

    def test_reads_gitea_config_template(self):
        """Verifies Gitea config template is read from correct path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/gitea/app.ini",
                )
            ],
        )

    def test_config_template_read_failure_results_in_failure(self):
        """Verifies template read failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[str].fail("Fail")
        self.reader.read_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_config_template_read_failure_results_in_failure_notifications_flow(self):
        """Verifies error notification when template read fails."""
        # Arrange
        failure_result = OperationResult[str].fail("Fail")
        self.reader.read_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {"text": "Will read Gitea configurations template.", "type": "info"},
                {"text": "\tFailed to read gitea/app.ini template.", "type": "error"},
            ],
        )

    def test_writes_correct_config_content(self):
        """Verifies config content is written to correct path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/srv/gitea/config/app.ini", "gitea-config-content")],
        )

    def test_write_failure_results_in_operation_failure(self):
        """Verifies config write failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.file_system.write_text_result_map = {
            "/srv/gitea/config/app.ini": failure_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_write_failure_results_in_failure_notifications_flow(self):
        """Verifies error notification when config write fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.file_system.write_text_result_map = {
            "/srv/gitea/config/app.ini": failure_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {"text": "Will read Gitea configurations template.", "type": "info"},
                {"text": "\tReading Gitea configurations template succeeded.", "type": "success"},
                {"text": "Will install Gitea path if it does not exist.", "type": "info"},
                {"text": "\tInstall succeeded.", "type": "success"},
                {"text": "Gitea configuration does not exist. Will create it now.", "type": "info"},
                {"text": "\tFailed storing Gitea configuration.", "type": "error"},
            ],
        )

    def test_gitea_path_install_command_failure_results_in_operation_failure(self):
        """Verifies directory creation failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result_regex_map = {
            "umask 0137 && install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config": failure_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_gitea_path_install_command_failure_results_in_operation_failure_notifications_flow(
        self,
    ):
        """Verifies error notification when directory creation fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result_regex_map = {
            "umask 0137 && install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config": failure_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {"text": "Will read Gitea configurations template.", "type": "info"},
                {"text": "\tReading Gitea configurations template succeeded.", "type": "success"},
                {"text": "Will install Gitea path if it does not exist.", "type": "info"},
                {"text": "\tInstall failed.", "type": "error"},
            ],
        )

    def test_gitea_path_chown_command_failure_results_in_operation_failure(self):
        """Verifies permission setup failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result_regex_map = {
            "sudo chown 1000:1000 /srv/gitea/config/app.ini && sudo chmod 0640 /srv/gitea/config/app.ini": failure_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_gitea_path_chown_command_failure_results_in_operation_failure_notifications_flow(self):
        """Verifies error notification when permission setup fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Fail")
        self.controller.run_raw_commands_result_regex_map = {
            "sudo chown 1000:1000 /srv/gitea/config/app.ini && sudo chmod 0640 /srv/gitea/config/app.ini": failure_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Seeding Gitea app.ini if missing.", "type": "info"},
                {"text": "Will check Gitea configuration and create it if needed.", "type": "info"},
                {"text": "Will read Gitea configurations template.", "type": "info"},
                {"text": "\tReading Gitea configurations template succeeded.", "type": "success"},
                {"text": "Will install Gitea path if it does not exist.", "type": "info"},
                {"text": "\tInstall succeeded.", "type": "success"},
                {"text": "Gitea configuration does not exist. Will create it now.", "type": "info"},
                {"text": "\tSucceeded in saving Gitea configuration.", "type": "success"},
                {"text": "Will process Gitea permissions.", "type": "info"},
                {"text": "\tProcessing failed.", "type": "error"},
            ],
        )
