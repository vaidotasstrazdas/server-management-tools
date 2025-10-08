"""Mock Input Collection Service - test double for input collection operations."""

from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

from .input_collection_service_contract import InputCollectionServiceContract

T = TypeVar("T")


@dataclass
class ReadParams(Generic[T]):
    """
    Data class storing parameters from a read operation call.

    Attributes:
        title: The prompt message used in the read call.
        default_value: The default value provided in the read call.
        call_order: The sequential order of this call among all read operations.
    """

    title: str
    default_value: Optional[T] = None
    call_order: int = 0


class MockInputCollectionService(InputCollectionServiceContract):
    """
    Mock implementation of InputCollectionService for testing purposes.

    Tracks all read operations and their parameters, allowing tests to verify
    correct usage. Supports both static return values and dynamic callback functions.

    Attributes:
        read_str_params: List of parameters from all read_str calls.
        read_str_result: Static result to return from read_str calls.
        read_str_result_fn: Optional callback function for dynamic read_str results.
        read_int_params: List of parameters from all read_int calls.
        read_int_result: Static result to return from read_int calls.
        read_int_result_fn: Optional callback function for dynamic read_int results.
        call_order: Counter tracking the sequential order of all read operations.
    """

    def __init__(self):
        """Initialize the mock service with empty tracking lists and default values."""
        self.read_str_params: list[ReadParams[str]] = []
        self.read_str_result = ""
        self.read_str_result_fn: Optional[Callable[[int, str, Optional[str]], str]] = None
        self.read_int_params: list[ReadParams[int]] = []
        self.read_int_result = 0
        self.read_int_result_fn: Optional[Callable[[int, str, Optional[int]], int]] = None
        self.call_order = 0

    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        """
        Mock implementation of read_str that records call parameters.

        Args:
            title: The prompt message to record.
            default_value: The default value to record.

        Returns:
            Result from read_str_result_fn if set, otherwise read_str_result.
        """
        self.call_order = self.call_order + 1
        self.read_str_params.append(ReadParams(title, default_value, self.call_order))
        if self.read_str_result_fn is not None:
            return self.read_str_result_fn(self.call_order, title, default_value)
        return self.read_str_result

    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        """
        Mock implementation of read_int that records call parameters.

        Args:
            title: The prompt message to record.
            default_value: The default value to record.

        Returns:
            Result from read_int_result_fn if set, otherwise read_int_result.
        """
        self.call_order = self.call_order + 1
        self.read_int_params.append(ReadParams(title, default_value, self.call_order))
        if self.read_int_result_fn is not None:
            return self.read_int_result_fn(self.call_order, title, default_value)
        return self.read_int_result
