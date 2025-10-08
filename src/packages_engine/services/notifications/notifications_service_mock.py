"""Mock Notifications Service - test double for notification operations."""

from .notification_service_contract import NotificationsServiceContract


class MockNotificationsService(NotificationsServiceContract):
    """
    Mock implementation of NotificationsService for testing purposes.

    Tracks all notification calls and their parameters, allowing tests to verify
    correct notification usage without producing actual console output.

    Attributes:
        params: List of dictionaries containing notification type and text for each call.
    """

    params: list[object] = []

    def __init__(self):
        """Initialize the mock service with an empty tracking list."""
        self.params = []

    def info(self, text: str):
        """
        Record an info notification call.

        Args:
            text: The informational message to record.
        """
        self.params.append({"type": "info", "text": text})

    def error(self, text: str):
        """
        Record an error notification call.

        Args:
            text: The error message to record.
        """
        self.params.append({"type": "error", "text": text})

    def success(self, text: str):
        """
        Record a success notification call.

        Args:
            text: The success message to record.
        """
        self.params.append({"type": "success", "text": text})

    def warning(self, text: str):
        """
        Record a warning notification call.

        Args:
            text: The warning message to record.
        """
        self.params.append({"type": "warning", "text": text})
