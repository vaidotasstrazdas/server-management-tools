"""Mock Configuration Content Reader Service - test double for configuration content reading operations."""

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData

from .configuration_content_reader_service_contract import ConfigurationContentReaderServiceContract


@dataclass
class ReadParams:
    """
    Data class storing parameters from a read operation call.

    Attributes:
        content: The configuration content type requested.
        config: The configuration data used in the read call.
        template_path: The optional template path provided.
    """

    content: ConfigurationContent
    config: ConfigurationData
    template_path: Optional[str] = None


class MockConfigurationContentReaderService(ConfigurationContentReaderServiceContract):
    """
    Mock implementation of ConfigurationContentReaderService for testing purposes.

    Tracks all read operations and their parameters, allowing tests to verify
    correct usage. Supports both static return values and dynamic callback functions.

    Attributes:
        read_params: List of parameters from all read calls.
        read_result: Static result to return from read calls.
        read_result_fn: Optional callback function for dynamic read results.
    """

    def __init__(self):
        """Initialize the mock service with empty tracking lists and default values."""
        self.read_params: list[ReadParams] = []
        self.read_result = OperationResult[str].succeed("")
        self.read_result_fn: Optional[
            Callable[[ConfigurationContent, ConfigurationData, Optional[str]], OperationResult[str]]
        ] = None
        self.read_result_map: Dict[str, OperationResult[str]] = {}

    def read(
        self,
        content: ConfigurationContent,
        config: ConfigurationData,
        template_path: Optional[str] = None,
    ) -> OperationResult[str]:
        """
        Mock implementation of read that records call parameters.

        Args:
            content: The configuration content type to record.
            config: The configuration data to record.
            template_path: The optional template path to record.

        Returns:
            Result from read_result_fn if set, otherwise read_result.
        """
        self.read_params.append(ReadParams(content, config, template_path))

        if self.read_result_fn is not None:
            return self.read_result_fn(content, config, template_path)

        if template_path in self.read_result_map:
            return self.read_result_map[template_path]

        return self.read_result
