import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.autostart import (
    AutostartUbuntuConfigurationTask,
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


class TestAutostartUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: AutostartUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = AutostartUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"
        self.reader.read_result = OperationResult[str].succeed("autostart content")
        self.maxDiff = None

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_results_in_correct_notifications(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tautostart.pyz permissions verified", "type": "success"},
                {"text": "\tAutostart service template read successfully", "type": "success"},
                {"text": "Saving autostart configuration in the system.", "type": "info"},
                {"text": "\tAutostart service configuration saved successfully", "type": "success"},
                {"text": "Enabling autostart service", "type": "info"},
                {"text": "\tAutostart service enabled and started", "type": "success"},
            ],
        )

    def test_reads_autostart_config_template_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/autostart.service",
                )
            ],
        )

    def test_autostart_config_template_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_autostart_config_template_read_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tautostart.pyz permissions verified", "type": "success"},
                {"text": "\tFailed to read autostart service template", "type": "error"},
            ],
        )

    def test_autostart_config_is_saved_in_the_system(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/etc/systemd/system/autostart.service", "autostart content")],
        )

    def test_autostart_config_save_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_autostart_config_save_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tautostart.pyz permissions verified", "type": "success"},
                {"text": "\tAutostart service template read successfully", "type": "success"},
                {"text": "Saving autostart configuration in the system.", "type": "info"},
                {"text": "\tFailed to save/overwrite autostart service", "type": "error"},
            ],
        )

    def test_commands_to_enable_autostart_service_are_run(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    "sudo install -d -m 0755 /usr/local/sbin",
                    "sudo chown root:root /usr/local/sbin/autostart.pyz",
                    "sudo chmod 0755 /usr/local/sbin/autostart.pyz",
                ],
                [
                    "sudo chown root:root /etc/systemd/system/autostart.service",
                    "sudo chmod 0644 /etc/systemd/system/autostart.service",
                ],
                [
                    "sudo systemctl daemon-reload",
                    "sudo systemctl enable autostart.service",
                    "sudo systemctl start autostart.service",
                ],
            ],
        )

    def test_commands_to_enable_autostart_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_commands_to_enable_autostart_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tFailed to set autostart.pyz permissions", "type": "error"},
            ],
        )

    def test_command_to_configure_autostart_script_failure_results_in_failure_result(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0755 /usr/local/sbin"
        ] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_command_to_configure_autostart_service_failure_results_in_failure_result(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo chown root:root /etc/systemd/system/autostart.service"
        ] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_command_to_restart_daemon_failure_results_in_failure_result(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo systemctl daemon-reload"] = (
            fail_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_command_to_configure_autostart_script_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0755 /usr/local/sbin"
        ] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tFailed to set autostart.pyz permissions", "type": "error"},
            ],
        )

    def test_command_to_configure_autostart_service_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo chown root:root /etc/systemd/system/autostart.service"
        ] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tautostart.pyz permissions verified", "type": "success"},
                {"text": "\tAutostart service template read successfully", "type": "success"},
                {"text": "Saving autostart configuration in the system.", "type": "info"},
                {"text": "\tFailed to set unit permissions", "type": "error"},
            ],
        )

    def test_command_to_restart_daemon_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo systemctl daemon-reload"] = (
            fail_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring autostart script", "type": "info"},
                {
                    "text": "Checking /usr/local/sbin/autostart.pyz presence and permissions",
                    "type": "info",
                },
                {"text": "\tautostart.pyz permissions verified", "type": "success"},
                {"text": "\tAutostart service template read successfully", "type": "success"},
                {"text": "Saving autostart configuration in the system.", "type": "info"},
                {"text": "\tAutostart service configuration saved successfully", "type": "success"},
                {"text": "Enabling autostart service", "type": "info"},
                {"text": "\tFailed to enable/start autostart service", "type": "error"},
            ],
        )
