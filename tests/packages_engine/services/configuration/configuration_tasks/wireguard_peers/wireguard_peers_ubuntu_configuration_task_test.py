"""Tests for WireguardPeersUbuntuConfigurationTask.

Verifies WireGuard server and client key/IP generation on Ubuntu.
"""
import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_tasks.wireguard_peers import (
    WireguardPeersUbuntuConfigurationTask,
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


class TestWireguardPeersUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for WireguardPeersUbuntuConfigurationTask.

    Tests WireGuard key pair generation and IP assignment for server and clients.
    """
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: WireguardPeersUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = WireguardPeersUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.wireguard_client_names = ["client_one", "client_two"]
        self.data.clients_data_dir = "/dev/usb/wireguard_clients"

        self.file_system.path_exists_result_map = {
            "/etc/wireguard/server.key": False,
            "/etc/wireguard/server.pub": False,
            "/etc/wireguard/server.ip": False,
            "/etc/wireguard/clients/client_one.key": False,
            "/etc/wireguard/clients/client_one.pub": False,
            "/etc/wireguard/clients/client_one.ip": False,
            "/etc/wireguard/clients/client_two.key": False,
            "/etc/wireguard/clients/client_two.pub": False,
            "/etc/wireguard/clients/client_two.ip": False,
        }

        self.file_system.write_text_result_map = {
            "/etc/wireguard/server.ip": OperationResult[bool].succeed(True),
            "/etc/wireguard/clients/client_one.ip": OperationResult[bool].succeed(True),
            "/etc/wireguard/clients/client_two.ip": OperationResult[bool].succeed(True),
        }
        self.maxDiff = None

    def test_happy_path(self):
        """Verify successful WireGuard peer configuration."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_has_correct_notifications_flow(self):
        """Verify correct notification sequence during successful configuration."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {
                    "text": "Preparing WireGuard server, clients configuration and keys.",
                    "type": "info",
                },
                {
                    "text": "Configuring permissions for the WireGuard configurations directory.",
                    "type": "info",
                },
                {
                    "text": "Configuring permissions for the WireGuard configurations directory "
                    "was successful.",
                    "type": "success",
                },
                {
                    "text": "Will generate WireGuard configuration data files for server and "
                    "clients now.",
                    "type": "info",
                },
                {"text": 'Generating configuration for the "/server".', "type": "info"},
                {
                    "text": 'WireGuard configuration for the "/server" has been generated '
                    "successfully.",
                    "type": "success",
                },
                {"text": 'Writing IP for the "/server"', "type": "info"},
                {"text": 'Writing IP for the "/server" succeeded', "type": "success"},
                {"text": 'Chmodding "/etc/wireguard/server.ip".', "type": "info"},
                {"text": 'Chmodding "/etc/wireguard/server.ip" successful.', "type": "success"},
                {"text": 'Generating configuration for the "/clients/client_one".', "type": "info"},
                {
                    "text": 'WireGuard configuration for the "/clients/client_one" has been '
                    "generated successfully.",
                    "type": "success",
                },
                {"text": 'Writing IP for the "/clients/client_one"', "type": "info"},
                {"text": 'Writing IP for the "/clients/client_one" succeeded', "type": "success"},
                {"text": 'Chmodding "/etc/wireguard/clients/client_one.ip".', "type": "info"},
                {
                    "text": 'Chmodding "/etc/wireguard/clients/client_one.ip" successful.',
                    "type": "success",
                },
                {"text": 'Generating configuration for the "/clients/client_two".', "type": "info"},
                {
                    "text": 'WireGuard configuration for the "/clients/client_two" has been '
                    "generated successfully.",
                    "type": "success",
                },
                {"text": 'Writing IP for the "/clients/client_two"', "type": "info"},
                {"text": 'Writing IP for the "/clients/client_two" succeeded', "type": "success"},
                {"text": 'Chmodding "/etc/wireguard/clients/client_two.ip".', "type": "info"},
                {
                    "text": 'Chmodding "/etc/wireguard/clients/client_two.ip" successful.',
                    "type": "success",
                },
            ],
        )

    def test_configures_permissions(self):
        """Verify WireGuard directories are created with correct permissions."""
        # Act
        self.task.configure(self.data)

        # Assert
        group = self.controller.find_first_raw_commands_group("sudo install")
        self.assertEqual(
            group, ["sudo install -d -m 0700 -o root -g root /etc/wireguard /etc/wireguard/clients"]
        )

    def test_produces_correct_notifications_flow_on_faiure_to_configure_permissions(self):
        """Verify error notifications when directory permission setup fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0700 -o root -g root /etc/wireguard /etc/wireguard/clients"
        ] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {
                    "text": "Preparing WireGuard server, clients configuration and keys.",
                    "type": "info",
                },
                {
                    "text": "Configuring permissions for the WireGuard configurations directory.",
                    "type": "info",
                },
                {
                    "text": "Failed to configure permissions for the WireGuard configurations "
                    "directory.",
                    "type": "error",
                },
            ],
        )

    def test_produces_failure_result_on_failure_to_configure_permissions(self):
        """Verify task fails when directory permission setup fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0700 -o root -g root /etc/wireguard /etc/wireguard/clients"
        ] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_generates_configuration_for_server(self):
        """Verify server key pair is generated correctly."""
        self._configurations_generation_test("server")

    def test_generates_configuration_for_clients_case_1(self):
        """Verify first client key pair is generated correctly."""
        self._configurations_generation_test("clients/client_one")

    def test_generates_configuration_for_clients_case_2(self):
        """Verify second client key pair is generated correctly."""
        self._configurations_generation_test("clients/client_two")

    def test_protects_ip_path_for_server(self):
        """Verify server IP file permissions are set correctly."""
        self._ip_path_protection_test("server")

    def test_protects_ip_path_for_clients_case_1(self):
        """Verify first client IP file permissions are set correctly."""
        self._ip_path_protection_test("clients/client_one")

    def test_protects_ip_path_for_clients_case_2(self):
        """Verify second client IP file permissions are set correctly."""
        self._ip_path_protection_test("clients/client_two")

    def test_stores_correct_server_ip(self):
        """Verify server IP is written correctly."""
        self._ip_store_test("server.ip", "10.10.0.1")

    def test_stores_correct_ip_for_clients_case_1(self):
        """Verify first client IP is written correctly."""
        self._ip_store_test("clients/client_one.ip", "10.10.0.2")

    def test_stores_correct_ip_for_clients_case_2(self):
        """Verify second client IP is written correctly."""
        self._ip_store_test("clients/client_two.ip", "10.10.0.3")

    def test_does_not_generate_configuration_for_server_when_paths_exist(self):
        """Verify server keys are not regenerated when they exist."""
        self._configurations_not_generation_test("server")

    def test_does_not_generate_configuration_for_clients_case_1_when_paths_exist(self):
        """Verify first client keys are not regenerated when they exist."""
        self._configurations_not_generation_test("clients/client_one")

    def test_does_not_generate_configuration_for_clients_case_2_when_paths_exist(self):
        """Verify second client keys are not regenerated when they exist."""
        self._configurations_not_generation_test("clients/client_two")

    def test_does_not_protect_ip_path_for_server_when_paths_exist(self):
        """Verify server IP permissions not set when file exists."""
        self._ip_path_not_protection_test("server")

    def test_does_not_protect_ip_path_for_clients_case_1_when_paths_exist(self):
        """Verify first client IP permissions not set when file exists."""
        self._ip_path_not_protection_test("clients/client_one")

    def test_does_not_protect_ip_path_for_clients_case_2_when_paths_exist(self):
        """Verify second client IP permissions not set when file exists."""
        self._ip_path_not_protection_test("clients/client_two")

    def test_does_not_store_server_ip_when_paths_exist(self):
        """Verify server IP not written when file exists."""
        self._ip_not_store_test("server")

    def test_does_not_store_ip_for_clients_case_1_when_paths_exist(self):
        """Verify first client IP not written when file exists."""
        self._ip_not_store_test("clients/client_one")

    def test_does_not_store_ip_for_clients_case_2_when_paths_exist(self):
        """Verify second client IP not written when file exists."""
        self._ip_not_store_test("clients/client_two")

    def test_failure_on_generate_configuration_for_server(self):
        """Verify task fails when server key generation fails."""
        self._configurations_generation_fail_test("server")

    def test_failure_on_generate_configuration_for_clients_case_1(self):
        """Verify task fails when first client key generation fails."""
        self._configurations_generation_fail_test("clients/client_one")

    def test_failure_on_generate_configuration_for_clients_case_2(self):
        """Verify task fails when second client key generation fails."""
        self._configurations_generation_fail_test("clients/client_two")

    def test_failure_on_protect_ip_path_for_server(self):
        """Verify task fails when server IP chmod fails."""
        self._ip_protection_failure_test("server")

    def test_failure_on_protect_ip_path_for_clients_case_1(self):
        """Verify task fails when first client IP chmod fails."""
        self._ip_protection_failure_test("clients/client_one")

    def test_failure_on_protect_ip_path_for_clients_case_2(self):
        """Verify task fails when second client IP chmod fails."""
        self._ip_protection_failure_test("clients/client_two")

    def test_failure_on_store_server_ip(self):
        """Verify task fails when server IP write fails."""
        self._ip_store_failure_test("server")

    def test_failure_on_store_ip_for_clients_case_1(self):
        """Verify task fails when first client IP write fails."""
        self._ip_store_failure_test("clients/client_one")

    def test_failure_on_store_ip_for_clients_case_2(self):
        """Verify task fails when second client IP write fails."""
        self._ip_store_failure_test("clients/client_two")

    def test_failure_on_generate_configuration_for_server_notifications(self):
        """Verify error notifications when server key generation fails."""
        self._configurations_generation_fail_notifications_test("server")

    def test_failure_on_generate_configuration_for_clients_case_1_notifications(self):
        """Verify error notifications when first client key generation fails."""
        self._configurations_generation_fail_notifications_test("clients/client_one")

    def test_failure_on_generate_configuration_for_clients_case_2_notifications(self):
        """Verify error notifications when second client key generation fails."""
        self._configurations_generation_fail_notifications_test("clients/client_two")

    def test_failure_on_protect_ip_path_for_server_notifications(self):
        """Verify error notifications when server IP chmod fails."""
        self._ip_protection_failure_notifications_test("server")

    def test_failure_on_protect_ip_path_for_clients_case_1_notifications(self):
        """Verify error notifications when first client IP chmod fails."""
        self._ip_protection_failure_notifications_test("clients/client_one")

    def test_failure_on_protect_ip_path_for_clients_case_2_notifications(self):
        """Verify error notifications when second client IP chmod fails."""
        self._ip_protection_failure_notifications_test("clients/client_two")

    def test_failure_on_store_server_ip_notifications(self):
        """Verify error notifications when server IP write fails."""
        self._ip_store_failure_notifications_test("server")

    def test_failure_on_store_ip_for_clients_case_1_notifications(self):
        """Verify error notifications when first client IP write fails."""
        self._ip_store_failure_notifications_test("clients/client_one")

    def test_failure_on_store_ip_for_clients_case_2_notifications(self):
        """Verify error notifications when second client IP write fails."""
        self._ip_store_failure_notifications_test("clients/client_two")

    def _configurations_generation_test(self, expected_config_entity: str):
        # Act
        self.task.configure(self.data)

        # Assert
        group = self.controller.find_first_raw_commands_group(
            f"test -f /etc/wireguard/{expected_config_entity}.key"
        )
        self.assertEqual(
            group,
            [
                f"test -f /etc/wireguard/{expected_config_entity}.key || (umask 077 && wg genkey | sudo tee /etc/wireguard/{expected_config_entity}.key >/dev/null)",
                f"test -f /etc/wireguard/{expected_config_entity}.pub || (sudo cat /etc/wireguard/{expected_config_entity}.key | wg pubkey | sudo tee /etc/wireguard/{expected_config_entity}.pub >/dev/null)",
                f"sudo chmod 600 /etc/wireguard/{expected_config_entity}.key",
            ],
        )

    def _ip_path_protection_test(self, expected_config_entity: str):
        # Act
        self.task.configure(self.data)

        # Assert
        ip_path = f"/etc/wireguard/{expected_config_entity}.ip"
        command = f"sudo chmod 0644 {ip_path}"
        group = self.controller.find_first_raw_commands_group(command)
        self.assertEqual(
            group,
            [command],
        )

    def _ip_store_test(self, path_term: str, ip_expected: str):
        # Act
        self.task.configure(self.data)

        # Assert
        params = self.file_system.find_write_text_params(path_term)
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].text, ip_expected)

    def _configurations_not_generation_test(self, expected_config_entity: str):
        # Arrange
        self.file_system.path_exists_result_map = {
            f"/etc/wireguard/{expected_config_entity}.key": True,
            f"/etc/wireguard/{expected_config_entity}.pub": True,
            f"/etc/wireguard/{expected_config_entity}.ip": True,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        group = self.controller.find_first_raw_commands_group(
            f"test -f /etc/wireguard/{expected_config_entity}.key"
        )
        self.assertIsNone(group)

    def _ip_path_not_protection_test(self, expected_config_entity: str):
        # Arrange
        self.file_system.path_exists_result_map = {
            f"/etc/wireguard/{expected_config_entity}.key": True,
            f"/etc/wireguard/{expected_config_entity}.pub": True,
            f"/etc/wireguard/{expected_config_entity}.ip": True,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        ip_path = f"/etc/wireguard/{expected_config_entity}.ip"
        command = f"sudo chmod 0644 {ip_path}"
        group = self.controller.find_first_raw_commands_group(command)
        self.assertIsNone(group)

    def _ip_not_store_test(self, expected_config_entity: str):
        # Arrange
        self.file_system.path_exists_result_map = {
            f"/etc/wireguard/{expected_config_entity}.key": True,
            f"/etc/wireguard/{expected_config_entity}.pub": True,
            f"/etc/wireguard/{expected_config_entity}.ip": True,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        params = self.file_system.find_write_text_params(f"{expected_config_entity}.ip")
        self.assertEqual(len(params), 0)

    def _configurations_generation_fail_test(self, expected_config_entity: str):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            f"test -f /etc/wireguard/{expected_config_entity}.key"
        ] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _ip_protection_failure_test(self, expected_config_entity: str):
        # Arrange
        ip_path = f"/etc/wireguard/{expected_config_entity}.ip"
        command = f"sudo chmod 0644 {ip_path}"
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _ip_store_failure_test(self, expected_config_entity: str):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map[f"/etc/wireguard/{expected_config_entity}.ip"] = (
            fail_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _configurations_generation_fail_notifications_test(self, expected_config_entity: str):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            f"test -f /etc/wireguard/{expected_config_entity}.key"
        ] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications(
            f'"/{expected_config_entity}"'
        )
        self.assertEqual(
            related_notifications,
            [
                {
                    "type": "info",
                    "text": f'Generating configuration for the "/{expected_config_entity}".',
                },
                {
                    "type": "error",
                    "text": f'Failed to generate the WireGuard configuration for the "/{expected_config_entity}"',
                },
            ],
        )

    def _ip_protection_failure_notifications_test(self, expected_config_entity: str):
        # Arrange
        ip_path = f"/etc/wireguard/{expected_config_entity}.ip"
        command = f"sudo chmod 0644 {ip_path}"
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications(f"/{expected_config_entity}")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": f'Generating configuration for the "/{expected_config_entity}".',
                    "type": "info",
                },
                {
                    "text": f'WireGuard configuration for the "/{expected_config_entity}" has been generated '
                    "successfully.",
                    "type": "success",
                },
                {"text": f'Writing IP for the "/{expected_config_entity}"', "type": "info"},
                {
                    "text": f'Writing IP for the "/{expected_config_entity}" succeeded',
                    "type": "success",
                },
                {
                    "text": f'Chmodding "/etc/wireguard/{expected_config_entity}.ip".',
                    "type": "info",
                },
                {
                    "text": f'Chmodding "/etc/wireguard/{expected_config_entity}.ip" failed.',
                    "type": "error",
                },
            ],
        )

    def _ip_store_failure_notifications_test(self, expected_config_entity: str):
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map[f"/etc/wireguard/{expected_config_entity}.ip"] = (
            fail_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications(f"/{expected_config_entity}")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": f'Generating configuration for the "/{expected_config_entity}".',
                    "type": "info",
                },
                {
                    "text": f'WireGuard configuration for the "/{expected_config_entity}" has been generated '
                    "successfully.",
                    "type": "success",
                },
                {"text": f'Writing IP for the "/{expected_config_entity}"', "type": "info"},
                {"text": f'Writing IP for the "/{expected_config_entity}" failed', "type": "error"},
            ],
        )
