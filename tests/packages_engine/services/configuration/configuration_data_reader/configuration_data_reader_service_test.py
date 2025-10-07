"""Necessary imports to implement Configuration Data Reader Service Tests"""

import unittest
from typing import Any, Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_data_reader import (
    ConfigurationDataReaderService,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
    WriteJsonParams,
)
from packages_engine.services.input_collection.input_collection_service_mock import (
    MockInputCollectionService,
    ReadParams,
)

_str_values = ["s", "ip", "a", "b", "c", "d", "e", "f", "", "foo", "bar", "/mount/usb"]
_str_values_with_option = [
    "",
    "s",
    "ip",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "",
    "foo",
    "bar",
    "/mount/usb",
]


class ConfigurationDataReaderServiceTestData:
    """Test data for the configuration data reader tests."""

    stored_data_option = "y"


def _read_str_result(call_order: int, title: str, default_value: Optional[str]) -> str:
    # pylint: disable=unused-argument
    if title == "You have stored configuration data. Type 'y' if you want to use stored data.":
        return "y"

    return _str_values[call_order - 1]


def _read_str_result_with_option(call_order: int, title: str, default_value: Optional[str]) -> str:
    # pylint: disable=unused-argument
    if title == "You have stored configuration data. Type 'y' if you want to use stored data.":
        return ConfigurationDataReaderServiceTestData.stored_data_option

    return _str_values_with_option[call_order - 1]


def _read_int_result(call_order: int, title: str, default_value: Optional[int]) -> int:
    # pylint: disable=unused-argument
    return 2


class TestConfigurationDataReaderService(unittest.TestCase):
    """Configuration Data Reader Service Tests"""

    input_collection: MockInputCollectionService
    file_system: MockFileSystemService
    service: ConfigurationDataReaderService
    option_data: ConfigurationData
    input_data: ConfigurationData

    def setUp(self):
        self.input_collection = MockInputCollectionService()
        self.file_system = MockFileSystemService()
        self.service = ConfigurationDataReaderService(self.input_collection, self.file_system)
        self.option_data = ConfigurationData(
            server_data_dir="srv",
            remote_ip_address="127.0.0.1",
            domain_name="internal.app",
            gitea_db_name="gitea-db",
            gitea_db_user="gitea-usr",
            gitea_db_password="gitea-pwd",
            pg_admin_email="user@example.com",
            pg_admin_password="pg-admin-pwd",
            num_wireguard_clients=2,
            wireguard_client_names=["limitless", "viewer"],
            clients_data_dir="/usr/local/share/clients",
        )
        self.input_data = ConfigurationData(
            server_data_dir="s",
            remote_ip_address="ip",
            domain_name="a",
            gitea_db_name="b",
            gitea_db_user="c",
            gitea_db_password="d",
            pg_admin_email="e",
            pg_admin_password="f",
            num_wireguard_clients=2,
            wireguard_client_names=["foo", "bar"],
            clients_data_dir="/mount/usb",
        )
        ConfigurationDataReaderServiceTestData.stored_data_option = "y"

    def test_correct_parameters_are_read(self):
        """Correct parameters are read."""
        # Arrange
        self.input_collection.read_str_result_fn = _read_str_result
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read()

        # Assert
        str_params = self.input_collection.read_str_params
        int_params = self.input_collection.read_int_params
        self.assertEqual(
            str_params,
            [
                ReadParams[str]("Server data directory", "srv", 1),
                ReadParams[str]("Remote Server IP Address", None, 2),
                ReadParams[str]("Domain name", "internal.app", 3),
                ReadParams[str]("Gitea database name", "gitea", 4),
                ReadParams[str]("Gitea database user", "gitea", 5),
                ReadParams[str]("Gitea database password", "123456", 6),
                ReadParams[str]("PostgreSQL Admin Email", "user@example.com", 7),
                ReadParams[str]("PostgreSQL Admin Password", "123456", 8),
                ReadParams[str]("Name of the Server Client #1", None, 10),
                ReadParams[str]("Name of the Server Client #2", None, 11),
                ReadParams[str]("Mounted directory for the Clients Configuration", None, 12),
            ],
        )
        self.assertEqual(
            int_params,
            [
                ReadParams[int]("Number of Server Clients", 2, 9),
            ],
        )

    def test_configuration_is_read_correctly(self):
        """Configuration is read correctly."""
        # Arrange
        self.input_collection.read_str_result_fn = _read_str_result
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read()

        # Assert
        self.assertEqual(
            result,
            self.input_data,
        )

    def test_configuration_is_stored_as_json(self):
        """Configuration is stored as JSON."""
        # Arrange
        self.input_collection.read_str_result_fn = _read_str_result
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read()

        # Assert
        self.assertEqual(
            self.file_system.write_json_params,
            [
                WriteJsonParams(
                    "/usr/local/share/args/configuration_data.json", self.input_data.as_object()
                )
            ],
        )

    def test_correct_parameters_are_read_with_option_when_selection_to_use_options_not_made(self):
        """Correct parameters are read with option when selection to use options not made."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "n"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        str_params = self.input_collection.read_str_params
        int_params = self.input_collection.read_int_params
        self.assertEqual(
            str_params,
            [
                ReadParams[str](
                    "You have stored configuration data. Type 'y' if you want to use stored data.",
                    None,
                    1,
                ),
                ReadParams[str]("Server data directory", "srv", 2),
                ReadParams[str]("Remote Server IP Address", None, 3),
                ReadParams[str]("Domain name", "internal.app", 4),
                ReadParams[str]("Gitea database name", "gitea", 5),
                ReadParams[str]("Gitea database user", "gitea", 6),
                ReadParams[str]("Gitea database password", "123456", 7),
                ReadParams[str]("PostgreSQL Admin Email", "user@example.com", 8),
                ReadParams[str]("PostgreSQL Admin Password", "123456", 9),
                ReadParams[str]("Name of the Server Client #1", None, 11),
                ReadParams[str]("Name of the Server Client #2", None, 12),
                ReadParams[str]("Mounted directory for the Clients Configuration", None, 13),
            ],
        )
        self.assertEqual(
            int_params,
            [
                ReadParams[int]("Number of Server Clients", 2, 10),
            ],
        )

    def test_correct_config_data_is_stored_as_json_with_option_when_to_use_option_choice_is_not_made(
        self,
    ):
        """Correct config data is stored as JSON with option when to use option choice is not made."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "n"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        self.assertEqual(
            self.file_system.write_json_params,
            [
                WriteJsonParams(
                    "/usr/local/share/args/configuration_data.json", self.input_data.as_object()
                )
            ],
        )

    def test_config_data_is_not_stored_as_json_with_option_when_to_use_option_choice_is_made(self):
        """Config data is not stored as JSON with option when to use option choice is made."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "y"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        self.assertEqual(
            self.file_system.write_json_params,
            [],
        )

    def test_correct_parameters_are_read_with_option_when_selection_to_use_options_made_case_1(
        self,
    ):
        """Correct parameters are read with option when selection to use options made (case 1)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "y"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        str_params = self.input_collection.read_str_params
        int_params = self.input_collection.read_int_params
        self.assertEqual(
            str_params,
            [
                ReadParams[str](
                    "You have stored configuration data. Type 'y' if you want to use stored data.",
                    None,
                    1,
                ),
            ],
        )
        self.assertEqual(
            int_params,
            [],
        )

    def test_correct_parameters_are_read_with_option_when_selection_to_use_options_made_case_2(
        self,
    ):
        """Correct parameters are read with option when selection to use options made (case 2)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "Y"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        str_params = self.input_collection.read_str_params
        int_params = self.input_collection.read_int_params
        self.assertEqual(
            str_params,
            [
                ReadParams[str](
                    "You have stored configuration data. Type 'y' if you want to use stored data.",
                    None,
                    1,
                ),
            ],
        )
        self.assertEqual(
            int_params,
            [],
        )

    def test_correct_parameters_are_read_with_option_when_selection_to_use_options_made_case_3(
        self,
    ):
        """Correct parameters are read with option when selection to use options made (case 3)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "  y "
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        self.service.read(self.option_data)

        # Assert
        str_params = self.input_collection.read_str_params
        int_params = self.input_collection.read_int_params
        self.assertEqual(
            str_params,
            [
                ReadParams[str](
                    "You have stored configuration data. Type 'y' if you want to use stored data.",
                    None,
                    1,
                ),
            ],
        )
        self.assertEqual(
            int_params,
            [],
        )

    def test_configuration_is_read_correctly_with_option_when_selection_to_use_options_not_made(
        self,
    ):
        """Configuration is read correctly with option when selection to use options not made."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "n"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read(self.option_data)

        # Assert
        self.assertEqual(
            result,
            self.input_data,
        )

    def test_configuration_is_read_correctly_with_option_when_selection_to_use_options_made_case_1(
        self,
    ):
        """Configuration is read correctly with option when selection to use options made (case 1)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "y"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read(self.option_data)

        # Assert
        self.assertEqual(result, self.option_data)

    def test_configuration_is_read_correctly_with_option_when_selection_to_use_options_made_case_2(
        self,
    ):
        """Configuration is read correctly with option when selection to use options made (case 2)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "Y"
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read(self.option_data)

        # Assert
        self.assertEqual(result, self.option_data)

    def test_configuration_is_read_correctly_with_option_when_selection_to_use_options_made_case_3(
        self,
    ):
        """Configuration is read correctly with option when selection to use options made (case 3)."""
        # Arrange
        ConfigurationDataReaderServiceTestData.stored_data_option = "  Y "
        self.input_collection.read_str_result_fn = _read_str_result_with_option
        self.input_collection.read_int_result_fn = _read_int_result

        # Act
        result = self.service.read(self.option_data)

        # Assert
        self.assertEqual(result, self.option_data)

    def test_loads_stored_from_correct_location(self):
        """Loading stored data loads everything from correct location."""
        # Act
        self.service.load_stored()

        # Assert
        self.assertEqual(
            self.file_system.read_json_params, ["/usr/local/share/args/configuration_data.json"]
        )

    def test_loading_stored_data_returns_none_on_operation_failure(self):
        """Loading stored data returns none on operation failure."""
        # Arrange
        self.file_system.read_json_result = OperationResult[Any].fail("Failure")

        # Act
        result = self.service.load_stored()

        # Assert
        self.assertEqual(result, None)

    def test_loading_stored_data_returns_none_on_no_data(self):
        """Loading stored data returns none on no data."""
        # Arrange
        self.file_system.read_json_result = OperationResult[Any].succeed(None)

        # Act
        result = self.service.load_stored()

        # Assert
        self.assertEqual(result, None)

    def test_loading_stored_data_returns_none_when_some_data_is_missing(self):
        """Loading stored data returns none when some data is missing."""
        # Arrange
        data_missing = self.option_data.as_object()
        del data_missing["server_data_dir"]
        self.file_system.read_json_result = OperationResult[Any].succeed(data_missing)

        # Act
        result = self.service.load_stored()

        # Assert
        self.assertEqual(result, None)

    def test_loading_stored_data_returns_data_on_success(self):
        """Loading stored data returns none on no data."""
        # Arrange
        self.file_system.read_json_result = OperationResult[Any].succeed(
            self.option_data.as_object()
        )

        # Act
        result = self.service.load_stored()

        # Assert
        self.assertEqual(result, self.option_data)
