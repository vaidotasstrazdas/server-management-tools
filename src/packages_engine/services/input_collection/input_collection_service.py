"""Input Collection Service - implementation for collecting user input via command line."""

from typing import Optional, TypeVar

from packages_engine.services.notifications import NotificationsServiceContract

from .input_collection_service_contract import InputCollectionServiceContract

T = TypeVar("T")


class InputCollectionService(InputCollectionServiceContract):
    """
    Input collection service implementation using command-line input.

    Collects user input from the command line with validation, automatic retry
    on invalid input, and support for default values. Uses NotificationsService
    to display error and warning messages to users.

    Attributes:
        notifications_service: Service for displaying user notifications.
    """

    def __init__(self, notifications_service: NotificationsServiceContract):
        """
        Initialize the input collection service with a notifications service.

        Args:
            notifications_service: Service to use for displaying notifications to the user.
        """
        self.notifications_service = notifications_service

    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        """
        Read a string value from user input with validation.

        Prompts the user for input and validates that it's not empty. If empty
        input is provided and a default value exists, returns the default.
        Otherwise, prompts again until valid input is received.

        Args:
            title: The prompt message to display to the user.
            default_value: Optional default value to use if user provides empty input.

        Returns:
            The trimmed string value entered by the user or the default value.
        """
        read_str_input = input(self._get_info(title, default_value)).strip()
        if read_str_input == "":
            if default_value is not None:
                return default_value
            self.notifications_service.warning("Value is empty. Try again.")
            return self.read_str(title, default_value)

        return read_str_input

    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        """
        Read an integer value from user input with validation.

        Prompts the user for input and validates that it's a valid integer. If empty
        input is provided and a default value exists, returns the default. If input
        is not a valid number, prompts again until valid input is received.

        Args:
            title: The prompt message to display to the user.
            default_value: Optional default value to use if user provides empty input.

        Returns:
            The integer value entered by the user or the default value.
        """
        read_int_input = input(self._get_info(title, default_value)).strip()
        if read_int_input == "":
            if default_value is not None:
                return default_value
            self.notifications_service.warning("Value is empty. Try again.")
            return self.read_int(title, default_value)

        if not read_int_input.isdigit():
            self.notifications_service.warning("Not a number. Try again.")
            return self.read_int(title, default_value)

        return int(read_int_input)

    def _get_info(self, title: str, default_value: Optional[T]) -> str:
        """
        Format the prompt message with optional default value hint.

        Args:
            title: The base prompt message.
            default_value: Optional default value to include in the prompt.

        Returns:
            Formatted prompt string with default value hint if applicable.
        """
        info = f"{title.strip()}"
        if default_value is not None:
            info = f"{info} (click Enter to set default={default_value})"
        info = f"{info}: "
        return info
