"""
Unit tests for the WireguardServerConfigContentReader class.

This module contains tests for the WireguardServerConfigContentReader, which generates
WireGuard server configuration files including all configured client peer configurations.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers.wireguard import (
    WireguardServerConfigContentReader,
)
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService


class TestWireguardServerConfigContentReader(unittest.TestCase):
    """
    Test suite for the WireguardServerConfigContentReader class.

    Tests generation of WireGuard server configurations, including reading server keys,
    templates, and client information to produce complete server configuration files.
    """

    config: ConfigurationData
    file_system: MockFileSystemService

    reader: WireguardServerConfigContentReader

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.config = ConfigurationData.default()
        self.config.server_data_dir = "ultimate"
        self.config.wireguard_client_names = ["developer", "viewer", "operator"]

        self.file_system = MockFileSystemService()
        self.reader = WireguardServerConfigContentReader(self.file_system)

        self.file_system.read_text_result_map = {
            "/etc/wireguard/server.key": OperationResult[str].succeed("private_server_key_value"),
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.server.conf": OperationResult[
                str
            ].succeed(
                """[Interface]
 PrivateKey = {{SERVER_KEY}}
Address = 10.10.0.1/24
ListenPort = 51820"""
            ),
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.client.conf": OperationResult[
                str
            ].succeed(
                """[Peer]
# Client Named '{{CLIENT_NAME}}'
PublicKey = {{CLIENT_PUBLIC_KEY}}
AllowedIPs = {{CLIENT_IP_ADDRESS}}/32"""
            ),
            "/etc/wireguard/clients/developer.endpoint": OperationResult[str].succeed("10.10.0.2"),
            "/etc/wireguard/clients/developer.pub": OperationResult[str].succeed(
                "developer_public_key_value"
            ),
            "/etc/wireguard/clients/viewer.endpoint": OperationResult[str].succeed("10.10.0.3"),
            "/etc/wireguard/clients/viewer.pub": OperationResult[str].succeed(
                "viewer_public_key_value"
            ),
            "/etc/wireguard/clients/operator.endpoint": OperationResult[str].succeed("10.10.0.4"),
            "/etc/wireguard/clients/operator.pub": OperationResult[str].succeed(
                "operator_public_key_value"
            ),
        }

    def test_happy_path_configuration(self):
        """Test that complete WireGuard server configuration is generated correctly with all clients."""
        # Act
        result = self.reader.read(self.config)

        # Assert
        self.assertEqual(
            result.data,
            """[Interface]
 PrivateKey = private_server_key_value
Address = 10.10.0.1/24
ListenPort = 51820

[Peer]
# Client Named 'developer'
PublicKey = developer_public_key_value
AllowedIPs = 10.10.0.2/32

[Peer]
# Client Named 'viewer'
PublicKey = viewer_public_key_value
AllowedIPs = 10.10.0.3/32

[Peer]
# Client Named 'operator'
PublicKey = operator_public_key_value
AllowedIPs = 10.10.0.4/32""",
        )

    def test_fails_when_server_private_key_not_read(self):
        """Test that read fails when server private key file cannot be read."""
        self._failed_path_test("/etc/wireguard/server.key")

    def test_fails_when_server_config_not_read(self):
        """Test that read fails when server configuration template cannot be read."""
        self._failed_path_test(
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.server.conf"
        )

    def test_fails_when_server_client_config_not_read(self):
        """Test that read fails when client configuration template cannot be read."""
        self._failed_path_test(
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.client.conf"
        )

    def test_fails_when_client_endpoint_not_read(self):
        """Test that read fails when a client endpoint file cannot be read."""
        self._failed_path_test("/etc/wireguard/clients/developer.endpoint")

    def test_fails_when_client_public_key_not_read(self):
        """Test that read fails when a client public key file cannot be read."""
        self._failed_path_test("/etc/wireguard/clients/operator.pub")

    def _failed_path_test(self, path: str):
        """
        Helper method to test failure scenarios when file reading fails.

        Args:
            path: The file path that should fail to read.
        """
        # Arrange
        failure = OperationResult[str].fail("Read failure")
        self.file_system.read_text_result_map[path] = failure

        # Act
        result = self.reader.read(self.config)

        # Assert
        self.assertEqual(result, failure)
