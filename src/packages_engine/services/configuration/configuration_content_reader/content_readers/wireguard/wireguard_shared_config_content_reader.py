
from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from packages_engine.services.configuration.configuration_content_reader.content_readers import ContentReader
from packages_engine.services.file_system import FileSystemServiceContract


class WireguardSharedConfigContentReader(ContentReader):
    def __init__(self, file_system: FileSystemServiceContract):
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        server_public_key_result = self.file_system.read_text(
            '/etc/wireguard/server.pub')
        if not server_public_key_result.success or server_public_key_result.data == None:
            return server_public_key_result.as_fail()
        server_public_key = server_public_key_result.data.strip()

        shared_config_tpl_result = self.file_system.read_text(
            f'/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.shared.conf')
        if not shared_config_tpl_result.success or shared_config_tpl_result.data == None:
            return shared_config_tpl_result.as_fail()
        shared_config_tpl = shared_config_tpl_result.data

        shared_configs = ''
        for client_name in config.wireguard_client_names:
            client_endpoint_result = self.file_system.read_text(
                f'/etc/wireguard/clients/{client_name}.endpoint')
            if not client_endpoint_result.success or client_endpoint_result.data == None:
                return client_endpoint_result.as_fail()

            client_private_key_result = self.file_system.read_text(
                f'/etc/wireguard/clients/{client_name}.key')
            if not client_private_key_result.success or client_private_key_result.data == None:
                return client_private_key_result.as_fail()

            client_endpoint = client_endpoint_result.data
            client_private_key = client_private_key_result.data

            shared_config = shared_config_tpl.replace(
                '{{CLIENT_NAME}}', client_name)
            shared_config = shared_config.replace(
                '{{CLIENT_PRIVATE_KEY}}', client_private_key)
            shared_config = shared_config.replace(
                '{{CLIENT_IP_ADDRESS}}', client_endpoint)
            shared_config = shared_config.replace(
                '{{SERVER_PUBLIC_KEY}}', server_public_key)
            shared_config = shared_config.replace(
                '{{REMOTE_IP_ADDRESS}}', config.remote_ip_address)
            shared_configs = shared_configs + '\n\n\n\n' + shared_config

        return OperationResult[str].succeed(shared_configs.strip())
