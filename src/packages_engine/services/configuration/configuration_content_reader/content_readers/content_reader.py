"""Content Reader Contract - defines interface for reading configuration content."""

from abc import ABC, abstractmethod
from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData


class ContentReader(ABC):
    """
    Abstract base class defining the contract for content readers.

    Provides a method to read and process configuration content from various sources,
    applying configuration data transformations as needed.
    """

    @abstractmethod
    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        """
        Read and process configuration content.

        Args:
            config: Configuration data to use for processing the content.
            path: Optional path to the content source.

        Returns:
            OperationResult containing the processed content string on success, or failure details.
        """
