"""Raw String Content Reader - reads and processes template files with configuration placeholders."""

from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.content_readers import (
    ContentReader,
)
from packages_engine.services.file_system import FileSystemServiceContract


class RawStringContentReader(ContentReader):
    """
    Content reader implementation for processing raw string templates.

    Reads text files and replaces configuration placeholders with actual values from
    ConfigurationData. Supports placeholders for server data directory, domain name,
    database credentials, and admin credentials.

    Attributes:
        file_system: Service for file system operations.
    """

    def __init__(self, file_system: FileSystemServiceContract):
        """
        Initialize the raw string content reader with a file system service.

        Args:
            file_system: Service to use for reading files.
        """
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        """
        Read template file and replace configuration placeholders with actual values.

        Replaces placeholders in the format {{PLACEHOLDER_NAME}} with corresponding
        values from the configuration data object.

        Args:
            config: Configuration data containing values for placeholder replacement.
            path: Path to the template file to read.

        Returns:
            OperationResult containing the processed content with replaced placeholders,
            or failure if path is missing or file cannot be read.
        """
        if path is None:
            return OperationResult[str].fail("Path cannot be empty")

        read_text_result = self.file_system.read_text(path)
        if not read_text_result.success or read_text_result.data is None:
            return read_text_result.as_fail()
        read_text_str = read_text_result.data

        result = read_text_str.replace("{{SERVER_DATA_DIR}}", config.server_data_dir)
        result = result.replace("{{DOMAIN_NAME}}", config.domain_name)
        result = result.replace("{{GITEA_DB_NAME}}", config.gitea_db_name)
        result = result.replace("{{GITEA_DB_USER}}", config.gitea_db_user)
        result = result.replace("{{GITEA_DB_PASSWORD}}", config.gitea_db_password)
        result = result.replace("{{PG_ADMIN_EMAIL}}", config.pg_admin_email)
        result = result.replace("{{PG_ADMIN_PASSWORD}}", config.pg_admin_password)

        return OperationResult[str].succeed(result)
