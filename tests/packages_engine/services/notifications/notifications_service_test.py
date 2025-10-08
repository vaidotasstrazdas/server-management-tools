"""
Unit tests for the NotificationsService class.

This module contains tests for the NotificationsService, which provides
colored console output for different notification types.
"""

import unittest
from unittest.mock import MagicMock, patch

from packages_engine.services.notifications import NotificationsService

PACKAGE_NAME = "packages_engine.services.notifications.notifications_service"


class TestNotificationsService(unittest.TestCase):
    """
    Test suite for the NotificationsService class.

    Tests all notification methods (info, error, success, warning) to verify
    they produce correctly formatted and colored console output.
    """

    service: NotificationsService

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.service = NotificationsService()

    @patch(f"{PACKAGE_NAME}.print")
    def test_info_prints_correct_text(self, mock_run: MagicMock):
        """Test info method prints message with blue ANSI color codes."""
        # Act
        self.service.info("info message")

        # Assert
        mock_run.assert_called_once_with("\x1b[94minfo message\x1b[0m")

    @patch(f"{PACKAGE_NAME}.print")
    def test_error_prints_correct_text(self, mock_run: MagicMock):
        """Test error method prints message with red ANSI color codes."""
        # Act
        self.service.error("error message")

        # Assert
        mock_run.assert_called_once_with("\x1b[91merror message\x1b[0m")

    @patch(f"{PACKAGE_NAME}.print")
    def test_success_prints_correct_text(self, mock_run: MagicMock):
        """Test success method prints message with green ANSI color codes."""
        # Act
        self.service.success("success message")

        # Assert
        mock_run.assert_called_once_with("\x1b[92msuccess message\x1b[0m")

    @patch(f"{PACKAGE_NAME}.print")
    def test_warning_prints_correct_text(self, mock_run: MagicMock):
        """Test warning method prints message with yellow ANSI color codes."""
        # Act
        self.service.warning("warning message")

        # Assert
        mock_run.assert_called_once_with("\x1b[93mwarning message\x1b[0m")
