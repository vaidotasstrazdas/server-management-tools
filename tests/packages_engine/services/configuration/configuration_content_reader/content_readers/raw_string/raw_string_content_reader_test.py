"""
Unit tests for the RawStringContentReader class.

This module contains tests for the RawStringContentReader, which reads template files
and replaces configuration placeholders with actual values from ConfigurationData.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers.raw_string import (
    RawStringContentReader,
)
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService


class TestRawStringContentReader(unittest.TestCase):
    """
    Test suite for the RawStringContentReader class.

    Tests template file reading and placeholder replacement for various configuration
    values including server directory, domain name, database credentials, and admin credentials.
    """

    config: ConfigurationData
    file_system: MockFileSystemService

    reader: RawStringContentReader

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.config = ConfigurationData.default()
        self.file_system = MockFileSystemService()
        self.reader = RawStringContentReader(self.file_system)

    def test_fails_when_path_is_unset(self):
        """Test that read fails when path parameter is None."""
        # Act
        result = self.reader.read(self.config, None)

        # Assert
        expected_result = OperationResult[str].fail("Path cannot be empty")
        self.assertEqual(result, expected_result)

    def test_fails_when_reading_data_fails(self):
        """Test that read fails when file system read operation fails."""
        # Arrange
        self.file_system.read_text_result = OperationResult[str].fail("I failed")

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        self.assertEqual(result, self.file_system.read_text_result)

    def test_reads_using_correct_path(self):
        """Test that reader calls file system with the correct path."""
        # Act
        self.reader.read(self.config, "/path")

        # Assert
        self.assertEqual(self.file_system.read_text_params, ["/path"])

    def test_config_multiple_configurations(self):
        """Test that multiple placeholders are replaced correctly in a single template."""
        # Arrange
        self.file_system.read_text_result = OperationResult[str].succeed(
            """
foo={{SERVER_DATA_DIR}}


bar={{PG_ADMIN_EMAIL}}
"""
        )
        self.config.server_data_dir = "/srv"
        self.config.pg_admin_email = "me@sample.com"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = OperationResult[str].succeed(
            """
foo=/srv


bar=me@sample.com
"""
        )
        self.assertEqual(result, expected_config)

    def test_config_server_data_dir_is_set(self):
        """Test that SERVER_DATA_DIR placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("SERVER_DATA_DIR")
        self.config.server_data_dir = "/srv"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.server_data_dir)
        self.assertEqual(result, expected_config)

    def test_config_domain_name_is_set(self):
        """Test that DOMAIN_NAME placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("DOMAIN_NAME")
        self.config.domain_name = "super.cool.app"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.domain_name)
        self.assertEqual(result, expected_config)

    def test_config_gitea_db_name_is_set(self):
        """Test that GITEA_DB_NAME placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("GITEA_DB_NAME")
        self.config.gitea_db_name = "giteadb"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.gitea_db_name)
        self.assertEqual(result, expected_config)

    def test_config_gitea_db_user_is_set(self):
        """Test that GITEA_DB_USER placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("GITEA_DB_USER")
        self.config.gitea_db_user = "giteadbuser"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.gitea_db_user)
        self.assertEqual(result, expected_config)

    def test_config_gitea_db_password_is_set(self):
        """Test that GITEA_DB_PASSWORD placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("GITEA_DB_PASSWORD")
        self.config.gitea_db_password = "giteadbuser-pwd-strong"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.gitea_db_password)
        self.assertEqual(result, expected_config)

    def test_config_pg_admin_email_is_set(self):
        """Test that PG_ADMIN_EMAIL placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("PG_ADMIN_EMAIL")
        self.config.pg_admin_email = "me@sample.com"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.pg_admin_email)
        self.assertEqual(result, expected_config)

    def test_config_pg_admin_password_is_set(self):
        """Test that PG_ADMIN_PASSWORD placeholder is replaced with configured value."""
        # Arrange
        self.file_system.read_text_result = self._config_tpl("PG_ADMIN_PASSWORD")
        self.config.pg_admin_password = "pg-admin-pwd-secret-and-strong"

        # Act
        result = self.reader.read(self.config, "/path")

        # Assert
        expected_config = self._config_result(self.config.pg_admin_password)
        self.assertEqual(result, expected_config)

    def _config_tpl(self, key: str) -> OperationResult[str]:
        """
        Create a template with placeholder for testing.

        Args:
            key: The placeholder key name to use in the template.

        Returns:
            OperationResult containing template with specified placeholder.
        """
        return OperationResult[str].succeed(
            f"""
foo={{{{{key}}}}}


bar={{{{{key}}}}}
"""
        )

    def _config_result(self, value: str) -> OperationResult[str]:
        """
        Create expected result with replaced value for testing.

        Args:
            value: The value that should replace the placeholder.

        Returns:
            OperationResult containing template with placeholder replaced by value.
        """
        return OperationResult[str].succeed(
            f"""
foo={value}


bar={value}
"""
        )
