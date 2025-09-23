import unittest

from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderService
from packages_engine.services.configuration.configuration_content_reader.content_readers.content_reader_mock import MockContentReader
from packages_engine.services.configuration.configuration_content_reader.content_readers.content_reader_mock import ReadParams
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService

class TestConfigurationContentReaderService(unittest.TestCase):
    config: ConfigurationData
    file_system: MockFileSystemService

    raw_reader: MockContentReader
    wireguard_server_config_reader: MockContentReader
    wireguard_shared_config_reader: MockContentReader

    service: ConfigurationContentReaderService

    def setUp(self):
        self.config = ConfigurationData.default()
        self.file_system = MockFileSystemService()

        self.raw_reader = MockContentReader()
        self.raw_reader.read_result = OperationResult[str].succeed('1')

        self.wireguard_server_config_reader = MockContentReader()
        self.wireguard_server_config_reader.read_result = OperationResult[str].succeed('2')

        self.wireguard_shared_config_reader = MockContentReader()
        self.wireguard_shared_config_reader.read_result = OperationResult[str].succeed('3')

        self.service = ConfigurationContentReaderService(
            self.file_system,
            self.raw_reader,
            self.wireguard_server_config_reader,
            self.wireguard_shared_config_reader)
    
    def test_raw_reader_is_used_on_raw_string_type(self):
        # Act
        self.service.read(ConfigurationContent.RAW_STRING, self.config, '/path')

        # Assert
        self.assertEqual(self.raw_reader.read_params, [ReadParams(self.config, '/path')])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [])
    
    def test_raw_reader_result_is_returned_on_raw_string_type(self):
        # Act
        result = self.service.read(ConfigurationContent.RAW_STRING, self.config, '/path')

        # Assert
        self.assertEqual(result, self.raw_reader.read_result)
    
    def test_wireguard_server_reader_is_used_on_wireguard_server_type(self):
        # Act
        self.service.read(ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.config, '/path')

        # Assert
        self.assertEqual(self.raw_reader.read_params, [])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [ReadParams(self.config)])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [])
    
    def test_wireguard_server_result_is_returned_on_wireguard_server_type(self):
        # Act
        result = self.service.read(ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.config, '/path')

        # Assert
        self.assertEqual(result, self.wireguard_server_config_reader.read_result)
    
    def test_wireguard_client_reader_is_used_on_wireguard_server_type(self):
        # Act
        self.service.read(ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.config, '/path')

        # Assert
        self.assertEqual(self.raw_reader.read_params, [])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [ReadParams(self.config)])
    
    def test_wireguard_client_result_is_returned_on_wireguard_server_type(self):
        # Act
        result = self.service.read(ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.config, '/path')

        # Assert
        self.assertEqual(result, self.wireguard_shared_config_reader.read_result)