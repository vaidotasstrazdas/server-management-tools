"""Mock Content Reader - test double for content reading operations."""

from dataclasses import dataclass
from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

from .content_reader import ContentReader


@dataclass
class ReadParams:
    """
    Data class storing parameters from a read operation call.

    Attributes:
        config: The configuration data used in the read call.
        path: The optional path provided in the read call.
    """

    config: ConfigurationData
    path: Optional[str] = None


class MockContentReader(ContentReader):
    """
    Mock implementation of ContentReader for testing purposes.

    Tracks all read operations and their parameters, allowing tests to verify
    correct usage. Provides configurable return values for testing different scenarios.

    Attributes:
        read_params: List of parameters from all read calls.
        read_result: The result to return from read calls.
    """

    def __init__(self):
        """Initialize the mock content reader with empty tracking lists and default values."""
        self.read_params: list[ReadParams] = []
        self.read_result = OperationResult[str].succeed("")

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        """
        Mock implementation of read that records call parameters.

        Args:
            config: The configuration data to record.
            path: The optional path to record.

        Returns:
            The configured read_result value.
        """
        self.read_params.append(ReadParams(config, path))
        return self.read_result
