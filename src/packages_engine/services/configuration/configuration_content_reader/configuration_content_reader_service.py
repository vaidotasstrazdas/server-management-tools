"""Configuration Content Reader Service - implementation for reading various configuration content types."""

from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.file_system import FileSystemServiceContract

from .configuration_content_reader_service_contract import ConfigurationContentReaderServiceContract
from .content_readers import ContentReader


class ConfigurationContentReaderService(ConfigurationContentReaderServiceContract):
    """
    Service implementation for reading configuration content.

    Routes read requests to appropriate specialized content readers based on the
    configuration content type. Supports raw string templates, WireGuard server
    configurations, and WireGuard client configurations.

    Attributes:
        file_system: Service for file system operations.
        raw_reader: Reader for raw string template processing.
        wireguard_server_config_reader: Reader for WireGuard server configurations.
        wireguard_shared_config_reader: Reader for WireGuard client configurations.
    """

    def __init__(
        self,
        file_system: FileSystemServiceContract,
        raw_reader: ContentReader,
        wireguard_server_config_reader: ContentReader,
        wireguard_shared_config_reader: ContentReader,
    ):
        """
        Initialize the configuration content reader service.

        Args:
            file_system: Service for file system operations.
            raw_reader: Content reader for raw string templates.
            wireguard_server_config_reader: Content reader for WireGuard server configs.
            wireguard_shared_config_reader: Content reader for WireGuard client configs.
        """
        self.file_system = file_system
        self.raw_reader = raw_reader
        self.wireguard_server_config_reader = wireguard_server_config_reader
        self.wireguard_shared_config_reader = wireguard_shared_config_reader

    def read(
        self,
        content: ConfigurationContent,
        config: ConfigurationData,
        template_path: Optional[str] = None,
    ) -> OperationResult[str]:
        """
        Read configuration content using the appropriate specialized reader.

        Routes the read request to the correct content reader based on content type.

        Args:
            content: The type of configuration content to read.
            config: Configuration data to use for processing.
            template_path: Optional path to a template file (used by raw string reader).

        Returns:
            OperationResult containing the processed configuration content,
            or failure if content type is undefined or reading fails.
        """
        if content == ConfigurationContent.RAW_STRING:
            return self.raw_reader.read(config, template_path)
        if content == ConfigurationContent.WIREGUARD_SERVER_CONFIG:
            return self.wireguard_server_config_reader.read(config)
        if content == ConfigurationContent.WIREGUARD_CLIENTS_CONFIG:
            return self.wireguard_shared_config_reader.read(config)
        return OperationResult[str].fail("Undefined content.")
