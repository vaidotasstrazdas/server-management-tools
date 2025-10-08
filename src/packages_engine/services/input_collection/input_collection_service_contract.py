"""Input Collection Service Contract - defines interface for collecting user input."""

from abc import ABC, abstractmethod
from typing import Optional


class InputCollectionServiceContract(ABC):
    """
    Abstract base class defining the contract for input collection services.

    Provides methods to collect string and integer input from users with
    support for default values and validation.
    """

    @abstractmethod
    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        """
        Read a string value from user input.

        Args:
            title: The prompt message to display to the user.
            default_value: Optional default value to use if user provides empty input.

        Returns:
            The string value entered by the user or the default value.
        """

    @abstractmethod
    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        """
        Read an integer value from user input.

        Args:
            title: The prompt message to display to the user.
            default_value: Optional default value to use if user provides empty input.

        Returns:
            The integer value entered by the user or the default value.
        """
