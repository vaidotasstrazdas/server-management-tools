"""WireGuard Shared Config Content Reader - generates WireGuard client configurations."""

from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers import (
    ContentReader,
)
from packages_engine.services.file_system import FileSystemServiceContract


class WireguardSharedConfigContentReader(ContentReader):
    """
    Content reader implementation for generating WireGuard client configurations.

    Reads the server's public key and shared configuration template, then generates
    individual client configurations for all configured clients. Each configuration
    includes the client's private key and connection details for the server.

    Attributes:
        file_system: Service for file system operations.
    """

    def __init__(self, file_system: FileSystemServiceContract):
        """
        Initialize the WireGuard shared config reader with a file system service.

        Args:
            file_system: Service to use for reading configuration files and keys.
        """
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        """
        Generate WireGuard client configurations for all configured clients.

        Reads server public key and shared config template, then iterates through
        all configured clients to generate individual client configurations.

        Args:
            config: Configuration data containing server data directory, client names, and remote IP.
            path: Optional path parameter (not used by this reader).

        Returns:
            OperationResult containing all client configurations separated by newlines,
            or failure if any required file cannot be read.
        """
        server_public_key_result = self.file_system.read_text("/etc/wireguard/server.pub")
        if not server_public_key_result.success or server_public_key_result.data is None:
            return server_public_key_result.as_fail()
        server_public_key = server_public_key_result.data.strip()

        shared_config_tpl_result = self.file_system.read_text(
            f"/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.shared.conf"
        )
        if not shared_config_tpl_result.success or shared_config_tpl_result.data is None:
            return shared_config_tpl_result.as_fail()
        shared_config_tpl = shared_config_tpl_result.data

        shared_configs = ""
        for client_name in config.wireguard_client_names:
            client_endpoint_result = self.file_system.read_text(
                f"/etc/wireguard/clients/{client_name}.ip"
            )
            if not client_endpoint_result.success or client_endpoint_result.data is None:
                return client_endpoint_result.as_fail()

            client_private_key_result = self.file_system.read_text(
                f"/etc/wireguard/clients/{client_name}.key"
            )
            if not client_private_key_result.success or client_private_key_result.data is None:
                return client_private_key_result.as_fail()

            client_endpoint = client_endpoint_result.data
            client_private_key = client_private_key_result.data

            shared_config = shared_config_tpl.replace("{{CLIENT_NAME}}", client_name)
            shared_config = shared_config.replace("{{CLIENT_PRIVATE_KEY}}", client_private_key)
            shared_config = shared_config.replace("{{CLIENT_IP_ADDRESS}}", client_endpoint)
            shared_config = shared_config.replace("{{SERVER_PUBLIC_KEY}}", server_public_key)
            shared_config = shared_config.replace("{{REMOTE_IP_ADDRESS}}", config.remote_ip_address)
            shared_configs = shared_configs + "\n\n\n\n" + shared_config

        return OperationResult[str].succeed(shared_configs.strip())
