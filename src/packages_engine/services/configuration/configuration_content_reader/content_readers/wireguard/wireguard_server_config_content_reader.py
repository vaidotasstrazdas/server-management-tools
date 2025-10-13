"""WireGuard Server Config Content Reader - generates WireGuard server configuration."""

from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers import (
    ContentReader,
)
from packages_engine.services.file_system import FileSystemServiceContract


class WireguardServerConfigContentReader(ContentReader):
    """
    Content reader implementation for generating WireGuard server configuration.

    Reads the server's private key, server configuration template, and client configuration
    template, then generates a complete WireGuard server configuration including all
    configured client peers.

    Attributes:
        file_system: Service for file system operations.
    """

    def __init__(self, file_system: FileSystemServiceContract):
        """
        Initialize the WireGuard server config reader with a file system service.

        Args:
            file_system: Service to use for reading configuration files and keys.
        """
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        """
        Generate WireGuard server configuration with all client peer configurations.

        Reads server private key, server config template, and client config template,
        then iterates through all configured clients to generate peer configurations.

        Args:
            config: Configuration data containing server data directory and client names.
            path: Optional path parameter (not used by this reader).

        Returns:
            OperationResult containing the complete WireGuard server configuration,
            or failure if any required file cannot be read.
        """
        server_key_result = self.file_system.read_text("/etc/wireguard/server.key")
        if not server_key_result.success or server_key_result.data is None:
            return server_key_result.as_fail()

        server_key = server_key_result.data.strip()
        server_config_tpl_result = self.file_system.read_text(
            f"/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.server.conf"
        )
        if not server_config_tpl_result.success or server_config_tpl_result.data is None:
            return server_config_tpl_result.as_fail()
        server_config_tpl = server_config_tpl_result.data

        server_config = server_config_tpl.replace("{{SERVER_KEY}}", server_key)

        client_config_tpl_result = self.file_system.read_text(
            f"/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.client.conf"
        )
        if not client_config_tpl_result.success or client_config_tpl_result.data is None:
            return client_config_tpl_result.as_fail()
        client_config_tpl = client_config_tpl_result.data

        clients_config = ""
        for client_name in config.wireguard_client_names:
            client_endpoint_result = self.file_system.read_text(
                f"/etc/wireguard/clients/{client_name}.ip"
            )
            if not client_endpoint_result.success or client_endpoint_result.data is None:
                return client_endpoint_result.as_fail()

            client_public_key_result = self.file_system.read_text(
                f"/etc/wireguard/clients/{client_name}.pub"
            )
            if not client_public_key_result.success or client_public_key_result.data is None:
                return client_public_key_result.as_fail()

            client_endpoint = client_endpoint_result.data
            client_public_key = client_public_key_result.data
            client_config = client_config_tpl.replace("{{CLIENT_NAME}}", client_name)
            client_config = client_config.replace("{{CLIENT_PUBLIC_KEY}}", client_public_key)
            client_config = client_config.replace("{{CLIENT_IP_ADDRESS}}", client_endpoint)
            clients_config = clients_config + "\n\n" + client_config

        full_config = server_config + clients_config

        return OperationResult[str].succeed(full_config)
