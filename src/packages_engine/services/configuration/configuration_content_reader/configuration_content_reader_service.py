from typing import Optional

from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult
from packages_engine.services.file_system import FileSystemServiceContract

from .configuration_content_reader_service_contract import ConfigurationContentReaderServiceContract

class ConfigurationFileService(ConfigurationContentReaderServiceContract):
    def __init__(self, file_system: FileSystemServiceContract):
        self.file_system = file_system

    def read(self, content: ConfigurationContent, config: ConfigurationData, template_path: Optional[str]) -> OperationResult[str]:
        read_text_str: Optional[str] = None
        if template_path != None:
            read_text_result = self.file_system.read_text(template_path)
            if not read_text_result.success:
                return read_text_result.as_fail()
            read_text_str = read_text_result.data
        
        if content == ConfigurationContent.RAW_STRING and read_text_str != None:
            return self._read_raw_string(read_text_str, config)
        elif content == ConfigurationContent.WIREGUARD_SERVER_CONFIG:
            return self._read_wireguard_server_config(config)
        elif content == ConfigurationContent.WIREGUARD_CLIENTS_CONFIG:
            return self._read_wireguard_clients_config(config)

        return OperationResult[str].succeed('')
    
    def _read_raw_string(self, text_str: str, config: ConfigurationData) -> OperationResult[str]:
        new_text = text_str.replace('{{SERVER_DATA_DIR}}', config.server_data_dir)
        new_text = text_str.replace('{{DOMAIN_NAME}}', config.domain_name)
        new_text = new_text.replace('{{GITEA_DB_NAME}}', config.gitea_db_name)
        new_text = new_text.replace('{{GITEA_DB_USER}}', config.gitea_db_user)
        new_text = new_text.replace('{{GITEA_DB_PASSWORD}}', config.gitea_db_password)
        new_text = new_text.replace('{{PG_ADMIN_EMAIL}}', config.pg_admin_email)
        new_text = new_text.replace('{{PG_ADMIN_PASSWORD}}', config.pg_admin_password)

        return OperationResult[str].succeed(new_text)
    
    def _read_wireguard_server_config(self, config: ConfigurationData) -> OperationResult[str]:
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
        
        full_config = server_config + '\n\n' + clients_config

        return OperationResult[str].succeed(full_config)
    
    def _read_wireguard_clients_config(self, config: ConfigurationData) -> OperationResult[str]:
        server_public_key_result = self.file_system.read_text('/etc/wireguard/server.key')
        if not server_public_key_result.success or server_public_key_result.data == None:
            return server_public_key_result.as_fail()
        server_public_key = server_public_key_result.data.strip()


        shared_config_tpl_result = self.file_system.read_text(f'/usr/local/share/{config.server_data_dir}/data/wireguard/wg0.shared.conf')
        if not shared_config_tpl_result.success or shared_config_tpl_result.data == None:
            return shared_config_tpl_result.as_fail()
        shared_config_tpl = shared_config_tpl_result.data

        shared_configs = ''
        for client_name in config.wireguard_client_names:
            client_endpoint_result = self.file_system.read_text(f'/etc/wireguard/clients/{client_name}.endpoint')
            if not client_endpoint_result.success or client_endpoint_result.data == None:
                return client_endpoint_result.as_fail()
            
            client_private_key_result = self.file_system.read_text(f'/etc/wireguard/clients/{client_name}.key')
            if not client_private_key_result.success or client_private_key_result.data == None:
                return client_private_key_result.as_fail()
            
            client_endpoint = client_endpoint_result.data
            client_private_key = client_private_key_result.data

            shared_config = shared_config_tpl.replace('{{CLIENT_NAME}}', client_name)
            shared_config = shared_config.replace('{{CLIENT_PRIVATE_KEY}}', client_private_key)
            shared_config = shared_config.replace('{{CLIENT_IP_ADDRESS}}', client_endpoint)
            shared_config = shared_config.replace('{{SERVER_PUBLIC_KEY}}', server_public_key)
            shared_config = shared_config.replace('{{REMOTE_IP_ADDRESS}}', config.remote_ip_address)
            shared_configs = shared_configs + '\n\n' + shared_config

        return OperationResult[str].succeed(shared_configs)