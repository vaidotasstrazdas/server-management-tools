import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.systemd import (
    SystemdUbuntuConfigurationTask,
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


class TestSystemdUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: SystemdUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = SystemdUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"

        self.file_system.write_text_result_map = {
            "/etc/systemd/resolved.conf.d/10-wg-split-dns.conf": OperationResult[bool].succeed(
                True
            ),
        }

        self.reader.read_result = OperationResult[str].succeed("split-dns-config")
        self.maxDiff = None

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will configure systemd now.", "type": "info"},
                {"text": "Reading split DNS configuration.", "type": "info"},
                {"text": "Reading split DNS configuration successful.", "type": "success"},
                {"text": "Writing split DNS configuration data.", "type": "info"},
                {
                    "text": "\tInstalling /etc/systemd/resolved.conf.d successful.",
                    "type": "success",
                },
                {"text": "\tWriting split DNS config data successful.", "type": "success"},
                {
                    "text": "Configuration split DNS configuration permissions, restarting "
                    "system.",
                    "type": "info",
                },
                {"text": "\tsystemd running with new configuration.", "type": "success"},
            ],
        )

    def test_reads_split_dns_config_template_correctly(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/systemd/resolved.conf.d/10-wg-split-dns.conf",
                )
            ],
        )

    def test_failure_to_read_split_dns_config_template_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_split_dns_config_template_results_in_correct_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will configure systemd now.", "type": "info"},
                {"text": "Reading split DNS configuration.", "type": "info"},
                {"text": "Reading split DNS configuration failed.", "type": "error"},
            ],
        )

    def test_installs_split_dns_config(self):
        # Act
        self.task.configure(self.data)

        # Assert
        command = "sudo install -d -m 0755 /etc/systemd/resolved.conf.d"
        group = self.controller.find_first_raw_commands_group(command)
        self.assertEqual(group, [command])

    def test_failure_to_install_split_dns_config_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        command = "sudo install -d -m 0755 /etc/systemd/resolved.conf.d"
        self.controller.run_raw_commands_result_regex_map[command] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_install_split_dns_config_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        command = "sudo install -d -m 0755 /etc/systemd/resolved.conf.d"
        self.controller.run_raw_commands_result_regex_map[command] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will configure systemd now.", "type": "info"},
                {"text": "Reading split DNS configuration.", "type": "info"},
                {"text": "Reading split DNS configuration successful.", "type": "success"},
                {"text": "Writing split DNS configuration data.", "type": "info"},
                {"text": "\tFailed installing /etc/systemd/resolved.conf.d.", "type": "error"},
            ],
        )

    def test_configures_split_dns_config_permissions(self):
        # Act
        self.task.configure(self.data)

        # Assert
        command = "sudo chown root:root"
        group = self.controller.find_first_raw_commands_group(command)
        self.assertEqual(
            group,
            [
                "sudo chown root:root /etc/systemd/resolved.conf.d/10-wg-split-dns.conf",
                "sudo chmod 0644 /etc/systemd/resolved.conf.d/10-wg-split-dns.conf",
                "sudo systemctl reload-or-restart systemd-resolved",
            ],
        )

    def test_failure_to_configure_split_dns_config_permissions_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        command = "sudo chown root:root"
        self.controller.run_raw_commands_result_regex_map[command] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_configure_split_dns_config_permissions_results_in_failure_notifications_flow(
        self,
    ):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        command = "sudo chown root:root"
        self.controller.run_raw_commands_result_regex_map[command] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will configure systemd now.", "type": "info"},
                {"text": "Reading split DNS configuration.", "type": "info"},
                {"text": "Reading split DNS configuration successful.", "type": "success"},
                {"text": "Writing split DNS configuration data.", "type": "info"},
                {
                    "text": "\tInstalling /etc/systemd/resolved.conf.d successful.",
                    "type": "success",
                },
                {"text": "\tWriting split DNS config data successful.", "type": "success"},
                {
                    "text": "Configuration split DNS configuration permissions, restarting "
                    "system.",
                    "type": "info",
                },
                {"text": "\tRunning systemd configuration failed.", "type": "error"},
            ],
        )

    def test_writes_dns_split_config(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams(
                    "/etc/systemd/resolved.conf.d/10-wg-split-dns.conf", "split-dns-config"
                )
            ],
        )

    def test_writing_dns_split_config_failure_results_in_fail(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map[
            "/etc/systemd/resolved.conf.d/10-wg-split-dns.conf"
        ] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_writing_dns_split_config_failure_results_in_fail_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map[
            "/etc/systemd/resolved.conf.d/10-wg-split-dns.conf"
        ] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will configure systemd now.", "type": "info"},
                {"text": "Reading split DNS configuration.", "type": "info"},
                {"text": "Reading split DNS configuration successful.", "type": "success"},
                {"text": "Writing split DNS configuration data.", "type": "info"},
                {
                    "text": "\tInstalling /etc/systemd/resolved.conf.d successful.",
                    "type": "success",
                },
                {"text": "\tWriting split DNS config data failed.", "type": "error"},
            ],
        )
