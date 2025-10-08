"""Notifications Service - implementation for displaying colored console notifications."""

from .notification_service_contract import NotificationsServiceContract


class NotificationsService(NotificationsServiceContract):
    """
    Notifications service implementation using colored console output.

    Displays notifications to the user via the console with ANSI color codes
    to distinguish between different notification types (info, error, success, warning).
    """

    def info(self, text: str):
        """
        Display an informational message in blue.

        Args:
            text: The informational message to display.
        """
        print(f"{_Colors.OKBLUE}{text}{_Colors.ENDC}")

    def error(self, text: str):
        """
        Display an error message in red.

        Args:
            text: The error message to display.
        """
        print(f"{_Colors.FAIL}{text}{_Colors.ENDC}")

    def success(self, text: str):
        """
        Display a success message in green.

        Args:
            text: The success message to display.
        """
        print(f"{_Colors.OKGREEN}{text}{_Colors.ENDC}")

    def warning(self, text: str):
        """
        Display a warning message in yellow.

        Args:
            text: The warning message to display.
        """
        print(f"{_Colors.WARNING}{text}{_Colors.ENDC}")


class _Colors:
    """ANSI color codes for terminal output formatting."""

    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
