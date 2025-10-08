"""
Unit tests for the InputCollectionService class.

This module contains comprehensive tests for the InputCollectionService, which provides
user input collection functionality via command line with validation, retry logic,
and support for default values.
"""

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from packages_engine.services.input_collection import InputCollectionService
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)

PACKAGE_NAME = "packages_engine.services.input_collection.input_collection_service"


class TestInputCollectionService(unittest.TestCase):
    """
    Test suite for the InputCollectionService class.

    Tests all input collection operations including string and integer reading,
    validation, retry logic, default value handling, and input trimming.
    Uses mocked input() and MockNotificationsService to isolate and verify service behavior.
    """

    service: InputCollectionService
    mock_notifications_service: MockNotificationsService

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.mock_notifications_service = MockNotificationsService()
        self.service = InputCollectionService(self.mock_notifications_service)

    @patch(f"{PACKAGE_NAME}.input", Mock(return_value="value"))
    def test_read_str_happy_path(self):
        """Test read_str returns the user-provided value in the happy path."""
        # Act
        result = self.service.read_str("Title")

        # Assert
        self.assertEqual(result, "value")

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_happy_path_input_makes_correct_calls(self, mock_input: MagicMock):
        """Test read_str calls input() with correctly formatted prompt."""
        # Arrange
        mock_input.side_effect = ["value"]

        # Act
        self.service.read_str("Title")

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call("Title: "),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_happy_path_notifications_makes_no_calls(self, mock_input: MagicMock):
        """Test read_str does not call notifications service when valid input is provided."""
        # Arrange
        mock_input.side_effect = ["value"]

        # Act
        self.service.read_str("Title")

        # Assert
        self.assertEqual(self.mock_notifications_service.params, [])

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_makes_necessary_warning_calls_when_input_is_empty_or_white_space(
        self, mock_input: MagicMock
    ):
        """Test read_str displays warning messages for empty and whitespace input."""
        # Arrange
        mock_input.side_effect = ["", "  ", "value"]

        # Act
        self.service.read_str("Title")

        # Assert
        self.assertEqual(
            self.mock_notifications_service.params,
            [
                {"type": "warning", "text": "Value is empty. Try again."},
                {"type": "warning", "text": "Value is empty. Try again."},
            ],
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_value_is_stripped(self, mock_input: MagicMock):
        """Test read_str trims leading and trailing whitespace from input."""
        # Arrange
        mock_input.side_effect = ["  value "]

        # Act
        result = self.service.read_str("Title")

        # Assert
        self.assertEqual(result, "value")

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_input_makes_calls_as_many_times_as_value_is_empty_or_white_space(
        self, mock_input: MagicMock
    ):
        """Test read_str retries input() for each empty or whitespace attempt."""
        # Arrange
        mock_input.side_effect = ["", " ", "", "value"]

        # Act
        self.service.read_str("Title")

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call("Title: "),
                call("Title: "),
                call("Title: "),
                call("Title: "),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_empty_string_first(self, mock_input: MagicMock):
        """Test read_str successfully retries after initial empty input."""
        # Arrange
        mock_input.side_effect = ["", "value"]

        # Act
        result = self.service.read_str("Title")

        # Assert
        self.assertEqual(result, "value")

    @patch(f"{PACKAGE_NAME}.input", Mock(return_value="10"))
    def test_read_int_happy_path(self):
        """Test read_int returns the user-provided integer value in the happy path."""
        # Act
        result = self.service.read_int("Title")

        # Assert
        self.assertEqual(result, 10)

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_happy_path_input_makes_correct_calls(self, mock_input: MagicMock):
        """Test read_int calls input() with correctly formatted prompt."""
        # Arrange
        mock_input.side_effect = ["10"]

        # Act
        self.service.read_int("Title")

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call("Title: "),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_happy_path_notifications_makes_no_calls(self, mock_input: MagicMock):
        """Test read_int does not call notifications service when valid input is provided."""
        # Arrange
        mock_input.side_effect = ["10"]

        # Act
        self.service.read_int("Title")

        # Assert
        self.assertEqual(self.mock_notifications_service.params, [])

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_makes_necessary_warning_calls_when_input_is_empty_or_white_space(
        self, mock_input: MagicMock
    ):
        """Test read_int displays warning messages for empty and whitespace input."""
        # Arrange
        mock_input.side_effect = ["", "  ", "10"]

        # Act
        self.service.read_int("Title")

        # Assert
        self.assertEqual(
            self.mock_notifications_service.params,
            [
                {"type": "warning", "text": "Value is empty. Try again."},
                {"type": "warning", "text": "Value is empty. Try again."},
            ],
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_value_is_stripped(self, mock_input: MagicMock):
        """Test read_int trims leading and trailing whitespace from input."""
        # Arrange
        mock_input.side_effect = ["  10 "]

        # Act
        result = self.service.read_int("Title")

        # Assert
        self.assertEqual(result, 10)

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_input_makes_calls_as_many_times_as_value_is_empty_or_white_space(
        self, mock_input: MagicMock
    ):
        """Test read_int retries input() for each empty or whitespace attempt."""
        # Arrange
        mock_input.side_effect = ["", " ", "", "10"]

        # Act
        self.service.read_int("Title")

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call("Title: "),
                call("Title: "),
                call("Title: "),
                call("Title: "),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_empty_string_first(self, mock_input: MagicMock):
        """Test read_int successfully retries after initial empty input."""
        # Arrange
        mock_input.side_effect = ["", "10"]

        # Act
        result = self.service.read_int("Title")

        # Assert
        self.assertEqual(result, 10)

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_makes_necessary_warning_calls_when_input_is_empty_white_space_or_invalid(
        self, mock_input: MagicMock
    ):
        """Test read_int displays appropriate warning messages for empty, whitespace, and non-numeric input."""
        # Arrange
        mock_input.side_effect = ["", "abc", "  ", "10"]

        # Act
        self.service.read_int("Title")

        # Assert
        self.assertEqual(
            self.mock_notifications_service.params,
            [
                {"type": "warning", "text": "Value is empty. Try again."},
                {"type": "warning", "text": "Not a number. Try again."},
                {"type": "warning", "text": "Value is empty. Try again."},
            ],
        )

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_int_default_value_is_returned_on_empty_string_when_default_value_provided(
        self, mock_input: MagicMock
    ):
        """Test read_int returns default value when empty input is provided and default is set."""
        # Arrange
        mock_input.side_effect = [
            "",
        ]

        # Act
        result = self.service.read_int("Title", 20)

        # Assert
        self.assertEqual(result, 20)

    @patch(f"{PACKAGE_NAME}.input")
    def test_read_str_default_value_is_returned_on_empty_string_when_default_value_provided(
        self, mock_input: MagicMock
    ):
        """Test read_str returns default value when empty input is provided and default is set."""
        # Arrange
        mock_input.side_effect = [
            "",
        ]

        # Act
        result = self.service.read_str("Title", "my default")

        # Assert
        self.assertEqual(result, "my default")
