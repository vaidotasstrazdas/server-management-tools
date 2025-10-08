"""Configuration Content Reader Service Contract - defines interface for reading configuration content."""

from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData


class ConfigurationContentReaderServiceContract(ABC):
    """
    Abstract base class defining the contract for configuration content reader services.

    Provides a method to read configuration content based on content type, delegating
    to appropriate specialized readers for different configuration formats.
    """

    @abstractmethod
    def read(
        self,
        content: ConfigurationContent,
        config: ConfigurationData,
        template_path: Optional[str] = None,
    ) -> OperationResult[str]:
        """
        Read configuration content using the appropriate reader for the content type.

        Args:
            content: The type of configuration content to read.
            config: Configuration data to use for processing the content.
            template_path: Optional path to a template file.

        Returns:
            OperationResult containing the processed configuration content,
            or failure if reading fails.
        """
