import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.wireguard import (
    WireguardUbuntuConfigurationTask,
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


class TestWireguardUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: WireguardUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = WireguardUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.wireguard_client_names = ["client_one", "client_two"]
        self.data.clients_data_dir = "/dev/usb/wireguard_clients"

        self.file_system.write_text_result_map = {
            "/etc/wireguard/wg0.conf": OperationResult[bool].succeed(True),
        }

        self.reader.read_result = OperationResult[str].succeed("wireguard-server-config")
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
                {"text": "Will Configure WireGuard now.", "type": "info"},
                {"text": "Reading WireGuard configuration.", "type": "info"},
                {"text": "Reading WireGuard configuration successful.", "type": "success"},
                {"text": "Writing WireGuard configuration.", "type": "info"},
                {"text": "Writing WireGuard configuration successful.", "type": "success"},
                {"text": "Fixing WireGuard configuration file permissions.", "type": "info"},
                {
                    "text": "Fixing WireGuard configuration file permissions successful.",
                    "type": "success",
                },
                {"text": "Starting wg0.", "type": "info"},
                {"text": "WireGuard configured and wg0 is up.", "type": "success"},
            ],
        )

    def test_executes_configuration_commands(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                ["sudo chmod 600 /etc/wireguard/wg0.conf"],
                [
                    "sudo bash -lc 'wg-quick strip wg0 > /run/wg0.conf && wg syncconf wg0 /run/wg0.conf || wg-quick up wg0'",
                    "sudo systemctl enable wg-quick@wg0",
                ],
            ],
        )

    def test_failure_to_configure_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_protect_wireguard_config_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo chmod 600 /etc/wireguard/wg0.conf"
        ] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_protect_wireguard_config_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo chmod 600 /etc/wireguard/wg0.conf"
        ] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will Configure WireGuard now.", "type": "info"},
                {"text": "Reading WireGuard configuration.", "type": "info"},
                {"text": "Reading WireGuard configuration successful.", "type": "success"},
                {"text": "Writing WireGuard configuration.", "type": "info"},
                {"text": "Writing WireGuard configuration successful.", "type": "success"},
                {"text": "Fixing WireGuard configuration file permissions.", "type": "info"},
                {
                    "text": "Fixing WireGuard configuration file permissions failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_restart_wireguard_config_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo bash"] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_restart_wireguard_config_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["sudo bash"] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will Configure WireGuard now.", "type": "info"},
                {"text": "Reading WireGuard configuration.", "type": "info"},
                {"text": "Reading WireGuard configuration successful.", "type": "success"},
                {"text": "Writing WireGuard configuration.", "type": "info"},
                {"text": "Writing WireGuard configuration successful.", "type": "success"},
                {"text": "Fixing WireGuard configuration file permissions.", "type": "info"},
                {
                    "text": "Fixing WireGuard configuration file permissions successful.",
                    "type": "success",
                },
                {"text": "Starting wg0.", "type": "info"},
                {"text": "Failed to start wg-quick@wg0.", "type": "error"},
            ],
        )

    def test_reads_correct_wireguard_configurations(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.data),
            ],
        )

    def test_failure_to_read_wireguard_server_configuration_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail("wireguard-server-config-read-failure")
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_read_wireguard_server_configuration_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[str].fail("wireguard-server-config-read-failure")
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will Configure WireGuard now.", "type": "info"},
                {"text": "Reading WireGuard configuration.", "type": "info"},
                {"text": "Failed reading WireGuard configuration.", "type": "error"},
            ],
        )

    def test_failure_to_save_wireguard_server_config_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Massive fail")
        self.file_system.write_text_result_map = {
            "/etc/wireguard/wg0.conf": fail_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_save_wireguard_server_config_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail("Massive fail")
        self.file_system.write_text_result_map = {
            "/etc/wireguard/wg0.conf": fail_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Will Configure WireGuard now.", "type": "info"},
                {"text": "Reading WireGuard configuration.", "type": "info"},
                {"text": "Reading WireGuard configuration successful.", "type": "success"},
                {"text": "Writing WireGuard configuration.", "type": "info"},
                {"text": "Failed writing WireGuard configuration.", "type": "error"},
            ],
        )

    def test_stores_server_config_correctly(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams("/etc/wireguard/wg0.conf", "wireguard-server-config"),
            ],
        )
