"""
Unit tests for the ConfigurationContentReaderService class.

This module contains tests for the ConfigurationContentReaderService, which routes
configuration content reading requests to appropriate specialized readers based on
content type.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_content_reader.content_readers.content_reader_mock import (
    MockContentReader,
    ReadParams,
)
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService


class TestConfigurationContentReaderService(unittest.TestCase):
    """
    Test suite for the ConfigurationContentReaderService class.

    Tests routing of configuration content read requests to appropriate specialized
    readers for different content types (raw strings, WireGuard server, WireGuard clients).
    """

    config: ConfigurationData
    file_system: MockFileSystemService

    raw_reader: MockContentReader
    wireguard_server_config_reader: MockContentReader
    wireguard_shared_config_reader: MockContentReader

    service: ConfigurationContentReaderService

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.config = ConfigurationData.default()
        self.file_system = MockFileSystemService()

        self.raw_reader = MockContentReader()
        self.raw_reader.read_result = OperationResult[str].succeed("1")

        self.wireguard_server_config_reader = MockContentReader()
        self.wireguard_server_config_reader.read_result = OperationResult[str].succeed("2")

        self.wireguard_shared_config_reader = MockContentReader()
        self.wireguard_shared_config_reader.read_result = OperationResult[str].succeed("3")

        self.service = ConfigurationContentReaderService(
            self.file_system,
            self.raw_reader,
            self.wireguard_server_config_reader,
            self.wireguard_shared_config_reader,
        )

    def test_raw_reader_is_used_on_raw_string_type(self):
        """Test that raw reader is invoked when RAW_STRING content type is requested."""
        # Act
        self.service.read(ConfigurationContent.RAW_STRING, self.config, "/path")

        # Assert
        self.assertEqual(self.raw_reader.read_params, [ReadParams(self.config, "/path")])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [])

    def test_raw_reader_result_is_returned_on_raw_string_type(self):
        """Test that raw reader's result is returned for RAW_STRING content type."""
        # Act
        result = self.service.read(ConfigurationContent.RAW_STRING, self.config, "/path")

        # Assert
        self.assertEqual(result, self.raw_reader.read_result)

    def test_wireguard_server_reader_is_used_on_wireguard_server_type(self):
        """Test that WireGuard server reader is invoked for WIREGUARD_SERVER_CONFIG content type."""
        # Act
        self.service.read(ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.config, "/path")

        # Assert
        self.assertEqual(self.raw_reader.read_params, [])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [ReadParams(self.config)])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [])

    def test_wireguard_server_result_is_returned_on_wireguard_server_type(self):
        """Test that WireGuard server reader's result is returned for WIREGUARD_SERVER_CONFIG content type."""
        # Act
        result = self.service.read(
            ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.config, "/path"
        )

        # Assert
        self.assertEqual(result, self.wireguard_server_config_reader.read_result)

    def test_wireguard_client_reader_is_used_on_wireguard_server_type(self):
        """Test that WireGuard client reader is invoked for WIREGUARD_CLIENTS_CONFIG content type."""
        # Act
        self.service.read(ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.config, "/path")

        # Assert
        self.assertEqual(self.raw_reader.read_params, [])
        self.assertEqual(self.wireguard_server_config_reader.read_params, [])
        self.assertEqual(self.wireguard_shared_config_reader.read_params, [ReadParams(self.config)])

    def test_wireguard_client_result_is_returned_on_wireguard_server_type(self):
        """Test that WireGuard client reader's result is returned for WIREGUARD_CLIENTS_CONFIG content type."""
        # Act
        result = self.service.read(
            ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.config, "/path"
        )

        # Assert
        self.assertEqual(result, self.wireguard_shared_config_reader.read_result)
