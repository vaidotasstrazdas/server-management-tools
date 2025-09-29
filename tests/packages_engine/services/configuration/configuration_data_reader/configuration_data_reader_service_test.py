import unittest

from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_data_reader import ConfigurationDataReaderService
from packages_engine.services.input_collection.input_collection_service_mock import MockInputCollectionService
from packages_engine.services.input_collection.input_collection_service_mock import ReadParams

_str_values = ['s', 'ip', 'a', 'b', 'c', 'd',
               'e', 'f', '', 'foo', 'bar', '/mount/usb']


def _read_str_result(call_order: int, title: str, default_value: Optional[str]) -> str:
    return _str_values[call_order - 1]


def _read_int_result(call_order: int, title: str, default_value: Optional[int]) -> int:
    return 2


class TestConfigurationDataReaderService(unittest.TestCase):
    mock_input_collection: MockInputCollectionService
    service: ConfigurationDataReaderService

    def setUp(self):
        self.mock_input_collection = MockInputCollectionService()
        self.service = ConfigurationDataReaderService(
            self.mock_input_collection)

    def test_correct_parameters_are_read(self):
        # Arrange
        self.mock_input_collection.read_str_result_fn = _read_str_result
        self.mock_input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read()

        # Assert
        str_params = self.mock_input_collection.read_str_params
        int_params = self.mock_input_collection.read_int_params
        self.assertEqual(str_params, [
            ReadParams[str]('Server data directory', 'srv', 1),
            ReadParams[str]('Remote Server IP Address', None, 2),
            ReadParams[str]('Domain name', 'internal.app', 3),
            ReadParams[str]('Gitea database name', 'gitea', 4),
            ReadParams[str]('Gitea database user', 'gitea', 5),
            ReadParams[str]('Gitea database password', '123456', 6),
            ReadParams[str]('PostgreSQL Admin Email', 'user@example.com', 7),
            ReadParams[str]('PostgreSQL Admin Password', '123456', 8),
            ReadParams[str]('Name of the Server Client #1', None, 10),
            ReadParams[str]('Name of the Server Client #2', None, 11),
            ReadParams[str](
                'Mounted directory for the Clients Configuration', None, 12),
        ])
        self.assertEqual(int_params, [
            ReadParams[int]('Number of Server Clients', 2, 9),
        ])

    def test_configuration_is_read_correctly(self):
        # Arrange
        self.mock_input_collection.read_str_result_fn = _read_str_result
        self.mock_input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read()

        # Assert
        self.assertEqual(
            result,
            ConfigurationData('s', 'ip', 'a', 'b', 'c', 'd',
                              'e', 'f', 2, ['foo', 'bar'], '/mount/usb')
        )
