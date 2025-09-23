
from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from packages_engine.services.configuration.configuration_content_reader.content_readers import ContentReader
from packages_engine.services.file_system import FileSystemServiceContract

class WireguardServerConfigContentReader(ContentReader):
    def __init__(self, file_system: FileSystemServiceContract):
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        server_key_result = self.file_system.read_text('/etc/wireguard/server.key')
        if not server_key_result.success or server_key_result.data == None:
            return server_key_result.as_fail()
        
        server_key = server_key_result.data.strip()
        server_config_tpl_result = self.file_system.read_text(f'/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.server.conf')
        if not server_config_tpl_result.success or server_config_tpl_result.data == None:
            return server_config_tpl_result.as_fail()
        server_config_tpl = server_config_tpl_result.data

        server_config = server_config_tpl.replace('{{SERVER_KEY}}', server_key)

        client_config_tpl_result = self.file_system.read_text(f'/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.client.conf')
        if not client_config_tpl_result.success or client_config_tpl_result.data == None:
            return client_config_tpl_result.as_fail()
        client_config_tpl = client_config_tpl_result.data

        clients_config = ''
        for client_name in config.wireguard_client_names:
            client_endpoint_result = self.file_system.read_text(f'/etc/wireguard/clients/{client_name}.endpoint')
            if not client_endpoint_result.success or client_endpoint_result.data == None:
                return client_endpoint_result.as_fail()
            
            client_public_key_result = self.file_system.read_text(f'/etc/wireguard/clients/{client_name}.pub')
            if not client_public_key_result.success or client_public_key_result.data == None:
                return client_public_key_result.as_fail()
            
            client_endpoint = client_endpoint_result.data
            client_public_key = client_public_key_result.data
            client_config = client_config_tpl.replace('{{CLIENT_NAME}}', client_name)
            client_config = client_config.replace('{{CLIENT_PUBLIC_KEY}}', client_public_key)
            client_config = client_config.replace('{{CLIENT_IP_ADDRESS}}', client_endpoint)
            clients_config = clients_config + '\n\n' + client_config
        
        full_config = server_config + clients_config

        return OperationResult[str].succeed(full_config)