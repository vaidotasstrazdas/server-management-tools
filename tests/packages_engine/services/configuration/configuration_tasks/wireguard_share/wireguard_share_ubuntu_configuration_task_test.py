"""Tests for WireguardShareUbuntuConfigurationTask.

Verifies WireGuard client configuration sharing on Ubuntu.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.wireguard_share import (
    WireguardShareUbuntuConfigurationTask,
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


class TestWireguardShareUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for WireguardShareUbuntuConfigurationTask.

    Tests WireGuard client configuration generation and sharing.
    """

    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: WireguardShareUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = WireguardShareUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.wireguard_client_names = ["client_one", "client_two"]
        self.data.clients_data_dir = "/dev/usb/wireguard_clients"

        self.file_system.write_text_result_map = {
            "/dev/usb/wireguard_clients/wg0_shared.conf": OperationResult[bool].succeed(True),
        }

        self.reader.read_result = OperationResult[str].succeed("wireguard-shared-config")
        self.maxDiff = None

    def test_happy_path(self):
        """Verify successful WireGuard configuration sharing."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        """Verify correct notification sequence during successful sharing."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing WireGuard configuration for the clients.", "type": "info"},
                {"text": "Reading WireGuard shared configuration.", "type": "info"},
                {"text": "Reading WireGuard shared configuration successful.", "type": "success"},
                {"text": "Writing WireGuard shared configuration.", "type": "info"},
                {"text": "Writing WireGuard shared configuration successful.", "type": "success"},
            ],
        )

    def test_reads_correct_wireguard_configurations(self):
        """Verify WireGuard client configuration is read correctly."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.data),
            ],
        )

    def test_failure_to_read_wireguard_clients_configuration_results_in_failure(self):
        """Verify task fails when configuration read fails."""
        # Arrange
        fail_result = OperationResult[str].fail("wireguard-clients-config-read-failure")
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_read_wireguard_clients_configuration_results_in_correct_notifications(self):
        """Verify error notifications when configuration read fails."""
        # Arrange
        fail_result = OperationResult[str].fail("wireguard-server-config-read-failure")
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing WireGuard configuration for the clients.", "type": "info"},
                {"text": "Reading WireGuard shared configuration.", "type": "info"},
                {"text": "Failed reading WireGuard shared configuration.", "type": "error"},
            ],
        )

    def test_failure_to_save_wireguard_clients_config_results_in_failure(self):
        """Verify task fails when configuration write fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Massive fail")
        self.file_system.write_text_result_map = {
            "/dev/usb/wireguard_clients/wg0_shared.conf": fail_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_save_wireguard_clients_config_results_in_correct_notifications(self):
        """Verify error notifications when configuration write fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Massive fail")
        self.file_system.write_text_result_map = {
            "/dev/usb/wireguard_clients/wg0_shared.conf": fail_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing WireGuard configuration for the clients.", "type": "info"},
                {"text": "Reading WireGuard shared configuration.", "type": "info"},
                {"text": "Reading WireGuard shared configuration successful.", "type": "success"},
                {"text": "Writing WireGuard shared configuration.", "type": "info"},
                {"text": "Failed writing WireGuard shared configuration.", "type": "error"},
            ],
        )

    def test_stores_clients_config_correctly(self):
        """Verify client configuration is written to correct location."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams(
                    "/dev/usb/wireguard_clients/wg0_shared.conf", "wireguard-shared-config"
                ),
            ],
        )
