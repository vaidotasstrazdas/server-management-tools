import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.dnsmasq import (
    DnsmasqUbuntuConfigurationTask,
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


class TestDnsmasqUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DnsmasqUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DnsmasqUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"
        self.reader.read_result = OperationResult[str].succeed("dnsmasq-config-result")
        self.maxDiff = None

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_results_in_correct_notifications_flow(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Dnsmasq Config template data.", "type": "info"},
                {"text": "\tReading Dnsmasq Config template data successful.", "type": "success"},
                {
                    "text": "\tWill configure using the following configuration:\n"
                    "\n"
                    "dnsmasq-config-result",
                    "type": "info",
                },
                {"text": "Writing Dnsmasq Config data.", "type": "info"},
                {"text": "\tWriting Dnsmasq Config data successful.", "type": "success"},
                {"text": "Validating Dnsmasq configuration.", "type": "info"},
                {"text": "\tDnsmasq config test OK.", "type": "success"},
                {
                    "text": "Configuration Dnsmasq configuration permissions, enabling and "
                    "(re)starting Dnsmasq.",
                    "type": "info",
                },
                {"text": "\tDnsmasq running with new configuration.", "type": "success"},
            ],
        )

    def test_reads_config_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/dnsmasq.conf",
                )
            ],
        )

    def test_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_read_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"type": "info", "text": "Reading Dnsmasq Config template data."},
                {"type": "error", "text": "\tReading Dnsmasq Config template data failed."},
            ],
        )

    def test_writes_config_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/etc/dnsmasq.d/internal.conf", "dnsmasq-config-result")],
        )

    def test_write_failure_result_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_write_failure_result_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Dnsmasq Config template data.", "type": "info"},
                {"text": "\tReading Dnsmasq Config template data successful.", "type": "success"},
                {
                    "text": "\tWill configure using the following configuration:\n"
                    "\n"
                    "dnsmasq-config-result",
                    "type": "info",
                },
                {"text": "Writing Dnsmasq Config data.", "type": "info"},
                {"text": "\tWriting Dnsmasq Config data failed.", "type": "error"},
            ],
        )

    def test_runs_correct_commands(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                ["sudo install -d -m 0755 /etc/dnsmasq.d"],
                ["sudo dnsmasq --test"],
                [
                    "sudo chown root:root /etc/dnsmasq.d/internal.conf",
                    "sudo chmod 0644 /etc/dnsmasq.d/internal.conf",
                    "sudo systemctl reset-failed dnsmasq || true",
                    "sudo systemctl enable --now dnsmasq",
                    "sudo install -d -m 0755 /etc/systemd/system/dnsmasq.service.d",
                    "sudo bash -lc 'cat > "
                    "/etc/systemd/system/dnsmasq.service.d/10-after-wg0.conf <<EOF\n"
                    "[Unit]\n"
                    "After=wg-quick@wg0.service\n"
                    "Wants=wg-quick@wg0.service\n"
                    "EOF'",
                    "sudo systemctl daemon-reload",
                    "sudo systemctl reload-or-restart dnsmasq",
                ],
            ],
        )

    def test_running_commands_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_running_commands_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Dnsmasq Config template data.", "type": "info"},
                {"text": "\tReading Dnsmasq Config template data successful.", "type": "success"},
                {
                    "text": "\tWill configure using the following configuration:\n"
                    "\n"
                    "dnsmasq-config-result",
                    "type": "info",
                },
                {"text": "Writing Dnsmasq Config data.", "type": "info"},
                {"text": "\tCreating /etc/dnsmasq.d failed.", "type": "error"},
            ],
        )
