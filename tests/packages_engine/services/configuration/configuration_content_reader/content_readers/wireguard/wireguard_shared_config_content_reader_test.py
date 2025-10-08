"""
Unit tests for the WireguardSharedConfigContentReader class.

This module contains tests for the WireguardSharedConfigContentReader, which generates
WireGuard client configuration files for distribution to all configured clients.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers.wireguard import (
    WireguardSharedConfigContentReader,
)
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService


class TestWireguardSharedConfigContentReader(unittest.TestCase):
    """
    Test suite for the WireguardSharedConfigContentReader class.

    Tests generation of WireGuard client configurations, including reading server public key,
    shared configuration template, and client information to produce complete client configs.
    """

    config: ConfigurationData
    file_system: MockFileSystemService

    reader: WireguardSharedConfigContentReader

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.config = ConfigurationData.default()
        self.config.server_data_dir = "ultimate"
        self.config.wireguard_client_names = ["developer", "viewer", "operator"]
        self.config.remote_ip_address = "127.0.0.1"

        self.file_system = MockFileSystemService()
        self.reader = WireguardSharedConfigContentReader(self.file_system)

        self.file_system.read_text_result_map = {
            "/etc/wireguard/server.pub": OperationResult[str].succeed("public_server_key_value"),
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.shared.conf": OperationResult[
                str
            ].succeed(
                """# Give this to the client named "{{CLIENT_NAME}}"
[Interface]
PrivateKey = {{CLIENT_PRIVATE_KEY}}
Address = {{CLIENT_IP_ADDRESS}}/24
DNS = 10.10.0.1

[Peer]
PublicKey = {{SERVER_PUBLIC_KEY}}
AllowedIPs = 10.10.0.1/32
Endpoint = {{REMOTE_IP_ADDRESS}}:51820
PersistentKeepalive = 25"""
            ),
            "/etc/wireguard/clients/developer.endpoint": OperationResult[str].succeed("10.10.0.2"),
            "/etc/wireguard/clients/developer.key": OperationResult[str].succeed(
                "developer_private_key_value"
            ),
            "/etc/wireguard/clients/viewer.endpoint": OperationResult[str].succeed("10.10.0.3"),
            "/etc/wireguard/clients/viewer.key": OperationResult[str].succeed(
                "viewer_private_key_value"
            ),
            "/etc/wireguard/clients/operator.endpoint": OperationResult[str].succeed("10.10.0.4"),
            "/etc/wireguard/clients/operator.key": OperationResult[str].succeed(
                "operator_private_key_value"
            ),
        }

    def test_happy_path_configuration(self):
        """Test that complete WireGuard client configurations are generated correctly for all clients."""
        # Act
        result = self.reader.read(self.config)

        # Assert
        self.assertEqual(
            result.data,
            """# Give this to the client named "developer"
[Interface]
PrivateKey = developer_private_key_value
Address = 10.10.0.2/24
DNS = 10.10.0.1

[Peer]
PublicKey = public_server_key_value
AllowedIPs = 10.10.0.1/32
Endpoint = 127.0.0.1:51820
PersistentKeepalive = 25



# Give this to the client named "viewer"
[Interface]
PrivateKey = viewer_private_key_value
Address = 10.10.0.3/24
DNS = 10.10.0.1

[Peer]
PublicKey = public_server_key_value
AllowedIPs = 10.10.0.1/32
Endpoint = 127.0.0.1:51820
PersistentKeepalive = 25



# Give this to the client named "operator"
[Interface]
PrivateKey = operator_private_key_value
Address = 10.10.0.4/24
DNS = 10.10.0.1

[Peer]
PublicKey = public_server_key_value
AllowedIPs = 10.10.0.1/32
Endpoint = 127.0.0.1:51820
PersistentKeepalive = 25""",
        )

    def test_fails_when_server_public_key_not_read(self):
        """Test that read fails when server public key file cannot be read."""
        self._failed_path_test("/etc/wireguard/server.pub")

    def test_fails_when_shared_config_not_read(self):
        """Test that read fails when shared configuration template cannot be read."""
        self._failed_path_test(
            f"/usr/local/share/{self.config.server_data_dir}/data/wireguard/wg0.shared.conf"
        )

    def test_fails_when_client_endpoint_not_read(self):
        """Test that read fails when a client endpoint file cannot be read."""
        self._failed_path_test("/etc/wireguard/clients/developer.endpoint")

    def test_fails_when_client_private_key_not_read(self):
        """Test that read fails when a client private key file cannot be read."""
        self._failed_path_test("/etc/wireguard/clients/operator.key")

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
