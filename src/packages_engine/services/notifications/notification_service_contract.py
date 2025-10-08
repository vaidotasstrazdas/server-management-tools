"""Notifications Service Contract - defines interface for user notifications."""

from abc import ABC, abstractmethod


class NotificationsServiceContract(ABC):
    """
    Abstract base class defining the contract for notification services.

    Provides methods to display different types of notifications to users
    including informational messages, errors, success messages, and warnings.
    """

    @abstractmethod
    def info(self, text: str):
        """
        Display an informational message to the user.

        Args:
            text: The informational message to display.
        """

    @abstractmethod
    def error(self, text: str):
        """
        Display an error message to the user.

        Args:
            text: The error message to display.
        """

    @abstractmethod
    def success(self, text: str):
        """
        Display a success message to the user.

        Args:
            text: The success message to display.
        """

    @abstractmethod
    def warning(self, text: str):
        """
        Display a warning message to the user.

        Args:
            text: The warning message to display.
        """
