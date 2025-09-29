from typing import Optional

from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult
from packages_engine.services.file_system import FileSystemServiceContract

from .configuration_content_reader_service_contract import ConfigurationContentReaderServiceContract
from .content_readers import ContentReader

class ConfigurationContentReaderService(ConfigurationContentReaderServiceContract):
    def __init__(self,
                 file_system: FileSystemServiceContract,
                 raw_reader: ContentReader,
                 wireguard_server_config_reader: ContentReader,
                 wireguard_shared_config_reader: ContentReader):
        self.file_system = file_system
        self.raw_reader = raw_reader
        self.wireguard_server_config_reader = wireguard_server_config_reader
        self.wireguard_shared_config_reader = wireguard_shared_config_reader

    def read(self, content: ConfigurationContent, config: ConfigurationData, template_path: Optional[str] = None) -> OperationResult[str]:
        if content == ConfigurationContent.RAW_STRING:
            return self.raw_reader.read(config, template_path)
        elif content == ConfigurationContent.WIREGUARD_SERVER_CONFIG:
            return self.wireguard_server_config_reader.read(config)
        elif content == ConfigurationContent.WIREGUARD_CLIENTS_CONFIG:
            return self.wireguard_shared_config_reader.read(config)