# pylint: disable=too-many-lines
"""
Unit tests for the FileSystemService class.

This module contains comprehensive tests for the FileSystemService, which provides
file system operations including reading/writing text and JSON files, creating directories,
changing permissions, copying paths, and removing locations.
"""

import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, create_autospec, patch

from packages_engine.models import OperationResult
from packages_engine.services.file_system import FileSystemService
from packages_engine.services.system_management.system_management_service_mock import (
    ExecuteCommandParams,
    MockSystemManagementService,
)

PACKAGE_NAME = "packages_engine.services.file_system.file_system_service"


class TestFileSystemServiceSpecData:
    """
    Helper class for creating mocked Path instances in FileSystemService tests.

    Provides factory methods to configure Path mocks with specific behaviors for
    different file system operations like reading, writing, directory creation,
    permission changes, and location removal.
    """

    def mock_read_text(self, exists: bool, is_file: bool, result: str, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for read_text operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            result: The text content to return when read_text is called.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.read_text.return_value = result
        mock_path.return_value = path_instance
        return path_instance

    def mock_write_text(self, exists: bool, is_file: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for write_text operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock with absolute path '/absolute-path.txt'.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.write_text.return_value = 0
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = "/absolute-path.txt"
        mock_path.return_value = path_instance
        return path_instance

    def mock_make_dir(self, exists: bool, is_file: bool, is_dir: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for directory creation operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            is_dir: Whether the path should be a directory.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock with absolute path '/absolute-path'.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.is_dir.return_value = is_dir
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = "/absolute-path"
        mock_path.return_value = path_instance
        return path_instance

    def mock_chmod(self, exists: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for chmod (permission change) operations.

        Args:
            exists: Whether the path should exist.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock with absolute path '/absolute-path'.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = "/absolute-path"
        mock_path.return_value = path_instance
        return path_instance

    def mock_remove_location(
        self, exists: bool, is_file: bool, is_dir: bool, mock_path: MagicMock
    ) -> Any:
        """
        Create a mocked Path instance configured for location removal operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            is_dir: Whether the path should be a directory.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock with absolute path '/absolute-path'.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.is_dir.return_value = is_dir
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = "/absolute-path"
        mock_path.return_value = path_instance
        return path_instance

    def mock_path_exists(self, exists: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for path existence check operations.

        Args:
            exists: Whether the path should exist.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        mock_path.return_value = path_instance
        return path_instance

    def mock_read_json(self, exists: bool, is_file: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for read_json operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        mock_path.return_value = path_instance
        return path_instance

    def mock_write_json(self, exists: bool, is_file: bool, mock_path: MagicMock) -> Any:
        """
        Create a mocked Path instance configured for write_json operations.

        Args:
            exists: Whether the path should exist.
            is_file: Whether the path should be a file.
            mock_path: The MagicMock to configure.

        Returns:
            Configured Path instance mock with absolute path '/absolute-path.json'.
        """
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = "/absolute-path.json"
        mock_path.return_value = path_instance
        return path_instance


class TestFileSystemService(unittest.TestCase):
    """
    Test suite for the FileSystemService class.

    Tests all file system operations including text/JSON file reading and writing,
    directory creation, permission changes, path existence checks, location removal,
    and path copying. Uses mocked Path instances and a mock system management service
    to isolate and verify the service behavior.
    """

    mock_system_management_service: MockSystemManagementService
    service: FileSystemService
    data: TestFileSystemServiceSpecData

    def setUp(self):
        """Initialize test fixtures before each test method."""
        self.mock_system_management_service = MockSystemManagementService()
        self.service = FileSystemService(self.mock_system_management_service)
        self.data = TestFileSystemServiceSpecData()

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_text_happy_path(self, mock_path: MagicMock):
        """Test read_text returns success with file content when file exists and is readable."""
        # Arrange
        self.data.mock_read_text(
            exists=True, is_file=True, result="text content", mock_path=mock_path
        )

        # Act
        result = self.service.read_text("file.txt")

        # Assert
        self.assertEqual(result, OperationResult[str].succeed("text content"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_text_happy_path_make_correct_calls_on_file_system(self, mock_path: MagicMock):
        """Test read_text makes correct sequence of Path method calls."""
        # Arrange
        self.data.mock_read_text(
            exists=True, is_file=True, result="text content", mock_path=mock_path
        )

        # Act
        self.service.read_text("file.txt")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("file.txt"),
                call().exists(),
                call().is_file(),
                call("file.txt"),
                call().read_text(encoding="utf-8"),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_text_fails_when_file_does_not_exist(self, mock_path: MagicMock):
        """Test read_text returns failure when the specified file does not exist."""
        # Arrange
        self.data.mock_read_text(
            exists=False, is_file=True, result="text content", mock_path=mock_path
        )

        # Act
        result = self.service.read_text("file.txt")

        # Assert
        self.assertEqual(result, OperationResult[str].fail("Path file.txt does not exist"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_text_fails_when_location_is_not_file(self, mock_path: MagicMock):
        """Test read_text returns failure when the location exists but is not a file."""
        # Arrange
        self.data.mock_read_text(
            exists=True, is_file=False, result="text content", mock_path=mock_path
        )

        # Act
        result = self.service.read_text("file.txt")

        # Assert
        self.assertEqual(result, OperationResult[str].fail("Path file.txt is not a file"))

    @patch(f"{PACKAGE_NAME}.json.load")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_json_happy_path(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_load: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test read_json returns success with JSON data when file exists and contains valid JSON."""
        # Arrange
        self.data.mock_read_json(exists=True, is_file=True, mock_path=mock_path)
        json_data: Any = {"key": "value", "number": 42}
        mock_json_load.return_value = json_data

        # Act
        result = self.service.read_json("file.json")

        # Assert
        self.assertEqual(result, OperationResult[Any].succeed(json_data))

    @patch(f"{PACKAGE_NAME}.json.load")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_json_happy_path_makes_correct_calls_on_file_system(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_load: MagicMock
    ):
        """Test read_json makes correct sequence of Path method calls and file operations."""
        # Arrange
        path_instance = self.data.mock_read_json(exists=True, is_file=True, mock_path=mock_path)
        json_data = {"key": "value"}
        mock_json_load.return_value = json_data

        # Act
        self.service.read_json("file.json")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("file.json"),
                call().exists(),
                call().is_file(),
                call("file.json"),
            ],
            any_order=False,
        )
        mock_open.assert_called_once_with(path_instance, "r", encoding="utf-8")
        mock_json_load.assert_called_once()

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_json_fails_when_location_is_not_file(self, mock_path: MagicMock):
        """Test read_json returns failure when the location exists but is not a file."""
        # Arrange
        self.data.mock_read_json(exists=True, is_file=False, mock_path=mock_path)

        # Act
        result = self.service.read_json("file.json")

        # Assert
        self.assertEqual(result, OperationResult[Any].fail("Path file.json is not a file"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_json_fails_when_file_does_not_exist(self, mock_path: MagicMock):
        """Test read_json returns failure when the specified file does not exist."""
        # Arrange
        self.data.mock_read_json(exists=False, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.read_json("file.json")

        # Assert
        self.assertEqual(result, OperationResult[Any].fail("Path file.json does not exist"))

    @patch(f"{PACKAGE_NAME}.json.load")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_read_json_fails_when_json_decode_error(
        self,
        mock_path: MagicMock,
        mock_open: MagicMock,
        mock_json_load: MagicMock,
    ):
        # pylint: disable=unused-argument
        """Test read_json returns failure when JSON decoding fails."""
        # Arrange
        self.data.mock_read_json(exists=True, is_file=True, mock_path=mock_path)
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        # Act
        result = self.service.read_json("file.json")

        # Assert
        self.assertEqual(
            result,
            OperationResult[Any].fail(
                "Error: Failed to decode JSON from the file. Path: file.json"
            ),
        )

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_happy_path(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json succeeds when writing to an existing file."""
        # Arrange
        self.data.mock_write_json(exists=True, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_json("file.json", {"key": "value"})

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_happy_path_makes_correct_calls_on_file_system(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        """Test write_json makes correct sequence of Path method calls and file operations."""
        # Arrange
        path_instance = self.data.mock_write_json(exists=True, is_file=True, mock_path=mock_path)
        json_data: Any = {"key": "value"}

        # Act
        self.service.write_json("file.json", json_data)

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("file.json"),
                call().exists(),
                call().is_file(),
                call().exists(),
            ],
            any_order=False,
        )
        mock_open.assert_called_once_with(path_instance, "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_fails_when_location_is_not_file(self, mock_path: MagicMock):
        """Test write_json fails when the location exists but is not a file."""
        # Arrange
        self.data.mock_write_json(exists=True, is_file=False, mock_path=mock_path)

        # Act
        result = self.service.write_json("file.json", {"key": "value"})

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Path file.json is not a file"))

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_creates_file_if_it_does_not_exist(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json creates a new file using sudo install command when file doesn't exist."""
        # Arrange
        self.data.mock_write_json(exists=False, is_file=True, mock_path=mock_path)

        # Act
        self.service.write_json("file.json", {"key": "value"})

        # Assert
        params = self.mock_system_management_service.execute_raw_command_params
        self.assertEqual(params, ["sudo install -Dv /dev/null /absolute-path.json"])

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_does_not_create_file_if_it_exists(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json skips file creation when file already exists."""
        # Arrange
        self.data.mock_write_json(exists=True, is_file=True, mock_path=mock_path)

        # Act
        self.service.write_json("file.json", {"key": "value"})

        # Assert
        params = self.mock_system_management_service.execute_raw_command_params
        self.assertEqual(params, [])

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_returns_failure_when_not_existing_file_creation_command_fails(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json returns failure when file creation command fails."""
        # Arrange
        self.mock_system_management_service.execute_raw_command_result = OperationResult[bool].fail(
            "failure"
        )
        self.data.mock_write_json(exists=False, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_json("file.json", {"key": "value"})

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("failure"))

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_returns_success_when_not_existing_file_is_created_successfully(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json returns success when a non-existing file is created successfully."""
        # Arrange
        self.mock_system_management_service.execute_raw_command_result = OperationResult[
            bool
        ].succeed(True)
        self.data.mock_write_json(exists=False, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_json("file.json", {"key": "value"})

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.json.dump")
    @patch(f"{PACKAGE_NAME}.open")
    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_json_fails_when_json_dump_fails(
        self, mock_path: MagicMock, mock_open: MagicMock, mock_json_dump: MagicMock
    ):
        # pylint: disable=unused-argument
        """Test write_json returns failure when json.dump fails with TypeError."""
        # Arrange
        self.data.mock_write_json(exists=True, is_file=True, mock_path=mock_path)
        mock_json_dump.side_effect = TypeError("Object is not JSON serializable")

        # Act
        result = self.service.write_json("file.json", {"key": "value"})

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Failed to save JSON data into the path: file.json")
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_happy_path(self, mock_path: MagicMock):
        """Test write_text succeeds when writing to an existing file."""
        # Arrange
        self.data.mock_write_text(exists=True, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_text("file.txt", "content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_happy_path_make_correct_calls_on_file_system(self, mock_path: MagicMock):
        """Test write_text makes correct sequence of Path method calls."""
        # Arrange
        self.data.mock_write_text(exists=True, is_file=True, mock_path=mock_path)

        # Act
        self.service.write_text("file.txt", "content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("file.txt"),
                call().exists(),
                call().is_file(),
                call().exists(),
                call().write_text("content", encoding="utf-8"),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_fails_when_location_is_not_file(self, mock_path: MagicMock):
        """Test write_text fails when the location exists but is not a file."""
        # Arrange
        self.data.mock_read_text(
            exists=True, is_file=False, result="text content", mock_path=mock_path
        )

        # Act
        result = self.service.write_text("file.txt", "content")

        # Assert
        self.assertEqual(result, OperationResult[str].fail("Path file.txt is not a file"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_creates_file_if_it_does_not_exist(self, mock_path: MagicMock):
        """Test write_text creates a new file using touch command when file doesn't exist."""
        # Arrange
        self.data.mock_write_text(exists=False, is_file=True, mock_path=mock_path)

        # Act
        self.service.write_text("file.txt", "content")

        # Assert
        params = self.mock_system_management_service.execute_raw_command_params
        self.assertEqual(params, ["sudo install -Dv /dev/null /absolute-path.txt"])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_does_not_create_file_if_it_exists(self, mock_path: MagicMock):
        """Test write_text skips file creation when file already exists."""
        # Arrange
        self.data.mock_write_text(exists=True, is_file=True, mock_path=mock_path)

        # Act
        self.service.write_text("file.txt", "content")

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_returns_success_when_not_existing_file_is_created_successfully(
        self, mock_path: MagicMock
    ):
        """Test write_text returns success when a non-existing file is created successfully."""
        # Arrange
        self.mock_system_management_service.execute_command_result = OperationResult[bool].succeed(
            True
        )
        self.data.mock_write_text(exists=False, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_text("file.txt", "content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_write_text_returns_failure_when_not_existing_filecreation_command_fails(
        self, mock_path: MagicMock
    ):
        """Test write_text returns failure when file creation command fails."""
        # Arrange
        self.mock_system_management_service.execute_raw_command_result = OperationResult[bool].fail(
            "failure"
        )
        self.data.mock_write_text(exists=False, is_file=True, mock_path=mock_path)

        # Act
        result = self.service.write_text("file.txt", "content")

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("failure"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_happy_path_when_dir_does_not_exist(self, mock_path: MagicMock):
        """Test make_dir succeeds when creating a new directory."""
        # Arrange
        self.data.mock_make_dir(exists=False, is_file=True, is_dir=True, mock_path=mock_path)

        # Act
        result = self.service.make_dir("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_happy_path_when_dir_exists(self, mock_path: MagicMock):
        """Test make_dir succeeds without action when directory already exists."""
        # Arrange
        self.data.mock_make_dir(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        result = self.service.make_dir("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_makes_correct_calls_on_file_system_when_dir_does_not_exist(
        self, mock_path: MagicMock
    ):
        """Test make_dir makes correct Path method calls when creating new directory."""
        # Arrange
        self.data.mock_make_dir(exists=False, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.make_dir("./content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_makes_correct_calls_on_file_system_when_dir_exists(
        self, mock_path: MagicMock
    ):
        """Test make_dir makes correct Path method calls when directory already exists."""
        # Arrange
        self.data.mock_make_dir(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.make_dir("./content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
                call().is_file(),
                call().is_dir(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_executes_command_when_dir_does_not_exist(self, mock_path: MagicMock):
        """Test make_dir executes mkdir command when directory does not exist."""
        # Arrange
        self.data.mock_make_dir(exists=False, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.make_dir("./content")

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["mkdir", "-p", "/absolute-path"])])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_does_not_execute_command_when_dir_exists(self, mock_path: MagicMock):
        """Test make_dir does not execute mkdir command when directory already exists."""
        # Arrange
        self.data.mock_make_dir(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.make_dir("./content")

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_returns_fail_when_existing_path_is_file(self, mock_path: MagicMock):
        """Test make_dir returns failure when path exists and is a file."""
        # Arrange
        self.data.mock_make_dir(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        result = self.service.make_dir("./content")

        # Assert
        self.assertEqual(
            result,
            OperationResult[bool].fail(
                "Path ./content is file, so can not make the directory out of it."
            ),
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_returns_fail_when_existing_path_is_not_directory(self, mock_path: MagicMock):
        """Test make_dir returns failure when path is neither file nor directory."""
        # Arrange
        self.data.mock_make_dir(exists=True, is_file=False, is_dir=False, mock_path=mock_path)

        # Act
        result = self.service.make_dir("./content")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Path ./content is not a file and not a directory.")
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_make_dir_returns_fail_when_creation_command_fails(self, mock_path: MagicMock):
        """Test make_dir returns failure when mkdir command execution fails."""
        # Arrange
        self.mock_system_management_service.execute_command_result = OperationResult[bool].fail(
            "failure"
        )
        self.data.mock_make_dir(exists=False, is_file=False, is_dir=False, mock_path=mock_path)

        # Actx
        result = self.service.make_dir("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("failure"))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_happy_path(self, mock_path: MagicMock):
        """Test chmod succeeds when changing permissions on an existing path."""
        # Arrange
        self.data.mock_chmod(exists=True, mock_path=mock_path)

        # Act
        result = self.service.chmod("./content", 777)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_happy_path_makes_correct_calls_on_file_system(self, mock_path: MagicMock):
        """Test chmod makes correct Path method calls."""
        # Arrange
        self.data.mock_chmod(exists=True, mock_path=mock_path)

        # Act
        self.service.chmod("./content", 777)

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_executes_correct_command(self, mock_path: MagicMock):
        """Test chmod executes correct command with proper permissions."""
        # Arrange
        self.data.mock_chmod(exists=True, mock_path=mock_path)

        # Act
        self.service.chmod("./content", 777)

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["chmod", "777", "/absolute-path"])])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_does_not_execute_command_on_not_existing_path(self, mock_path: MagicMock):
        """Test chmod does not execute command when path does not exist."""
        # Arrange
        self.data.mock_chmod(exists=False, mock_path=mock_path)

        # Act
        self.service.chmod("./content", 777)

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_returns_failure_when_path_does_not_exist(self, mock_path: MagicMock):
        """Test chmod returns failure when the path does not exist."""
        # Arrange
        self.data.mock_chmod(exists=False, mock_path=mock_path)

        # Act
        result = self.service.chmod("./content", 777)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Path ./content does not exist."))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_returns_success_when_command_succeeds(self, mock_path: MagicMock):
        """Test chmod returns success when the chmod command succeeds."""
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_chmod(exists=True, mock_path=mock_path)

        # Act
        result = self.service.chmod("./content", 777)

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_returns_failure_when_command_fails(self, mock_path: MagicMock):
        """Test chmod returns failure when the chmod command fails."""
        # Arrange
        command_result = OperationResult[bool].fail("Failure")
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_chmod(exists=True, mock_path=mock_path)

        # Act
        result = self.service.chmod("./content", 777)

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_happy_path_when_item_does_not_exist(self, mock_path: MagicMock):
        """Test remove_location succeeds without action when item does not exist."""
        # Arrange
        self.data.mock_remove_location(
            exists=False, is_file=False, is_dir=False, mock_path=mock_path
        )

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_makes_correct_calls_when_item_does_not_exist(
        self, mock_path: MagicMock
    ):
        """Test remove_location makes correct Path calls when item does not exist."""
        # Arrange
        self.data.mock_remove_location(
            exists=False, is_file=False, is_dir=False, mock_path=mock_path
        )

        # Act
        self.service.remove_location("./content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_happy_path_when_item_exists_as_file(self, mock_path: MagicMock):
        """Test remove_location succeeds when removing a file."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_makes_correct_calls_when_item_exists_as_file(
        self, mock_path: MagicMock
    ):
        """Test remove_location makes correct Path calls when removing a file."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        self.service.remove_location("./content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
                call().absolute(),
                call().as_posix(),
                call().is_file(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_happy_path_when_item_exists_as_folder(
        self, mock_path: MagicMock
    ):
        """Test remove_location succeeds when removing a directory."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_makes_correct_calls_when_item_exists_as_folder(
        self, mock_path: MagicMock
    ):
        """Test remove_location makes correct Path calls when removing a directory."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.remove_location("./content")

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call("./content"),
                call().exists(),
                call().absolute(),
                call().as_posix(),
                call().is_file(),
                call().is_dir(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_fails_when_location_is_neither_file_nor_dir(
        self, mock_path: MagicMock
    ):
        """Test remove_location fails when location is neither file nor directory."""
        # Arrange
        self.data.mock_remove_location(
            exists=True, is_file=False, is_dir=False, mock_path=mock_path
        )

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Location ./content is neither file nor directory.")
        )

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_file_succeeds_when_command_succeeds(self, mock_path: MagicMock):
        """Test remove_location succeeds when rm command succeeds for a file."""
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_remove_location(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_file_fails_when_command_fails(self, mock_path: MagicMock):
        """Test remove_location fails when rm command fails for a file."""
        # Arrange
        command_result = OperationResult[bool].fail("failure")
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_remove_location(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_file_executes_correct_command(self, mock_path: MagicMock):
        """Test remove_location executes correct rm command for a file."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=True, is_dir=False, mock_path=mock_path)

        # Act
        self.service.remove_location("./content")

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["rm", "/absolute-path"])])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_folder_succeeds_when_command_succeeds(
        self, mock_path: MagicMock
    ):
        """Test remove_location succeeds when rm command succeeds for a directory."""
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_remove_location(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_folder_fails_when_command_fails(self, mock_path: MagicMock):
        """Test remove_location fails when rm command fails for a directory."""
        # Arrange
        command_result = OperationResult[bool].fail("failure")
        self.mock_system_management_service.execute_command_result = command_result
        self.data.mock_remove_location(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        result = self.service.remove_location("./content")

        # Assert
        self.assertEqual(result, command_result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_chmod_remove_location_folder_executes_correct_command(self, mock_path: MagicMock):
        """Test remove_location executes correct rm command for a directory."""
        # Arrange
        self.data.mock_remove_location(exists=True, is_file=False, is_dir=True, mock_path=mock_path)

        # Act
        self.service.remove_location("./content")

        # Assert
        params = self.mock_system_management_service.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["rm", "-r", "/absolute-path"])])

    @patch(f"{PACKAGE_NAME}.Path")
    def test_path_exists_case_1(self, mock_path: MagicMock):
        """Test path_exists returns True when path exists."""
        # Arrange
        self.data.mock_path_exists(exists=True, mock_path=mock_path)

        # Act
        result = self.service.path_exists("./content")

        # Assert
        self.assertTrue(result)

    @patch(f"{PACKAGE_NAME}.Path")
    def test_path_exists_case_2(self, mock_path: MagicMock):
        """Test path_exists returns False when path does not exist."""
        # Arrange
        self.data.mock_path_exists(exists=False, mock_path=mock_path)

        # Act
        result = self.service.path_exists("./content")

        # Assert
        self.assertFalse(result)

    @patch(f"{PACKAGE_NAME}.Path.exists")
    def test_copy_path_happy_path(self, mock_path: MagicMock):
        """Test copy_path succeeds when source exists and destination doesn't."""
        # Arrange
        mock_path.side_effect = [True, False]

        # Act
        result = self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path.exists")
    def test_copy_path_results_in_error_when_starting_location_does_not_exist(
        self, mock_path: MagicMock
    ):
        """Test copy_path fails when source location does not exist."""
        # Arrange
        mock_path.side_effect = [False, False]

        # Act
        result = self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Path "from" does not exist'))

    @patch(f"{PACKAGE_NAME}.Path.exists")
    def test_copy_path_does_not_remove_location_copied_to_when_it_does_not_exist(
        self, mock_path: MagicMock
    ):
        """Test copy_path does not attempt removal when destination doesn't exist."""
        # Arrange
        mock_path.side_effect = [False, False]

        # Act
        self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(self.mock_system_management_service.execute_command_params, [])

    @patch(f"{PACKAGE_NAME}.Path.as_posix")
    @patch(f"{PACKAGE_NAME}.Path.exists")
    @patch(f"{PACKAGE_NAME}.Path.is_file")
    @patch(f"{PACKAGE_NAME}.Path.is_dir")
    def test_copy_path_removes_location_copied_to_when_it_exists_as_file(
        self,
        mock_is_dir: MagicMock,
        mock_is_file: MagicMock,
        mock_exists: MagicMock,
        mock_as_posix: MagicMock,
    ):
        """Test copy_path removes existing destination file before copying."""
        # Arrange
        mock_is_dir.side_effect = [False]
        mock_is_file.side_effect = [True]
        mock_exists.side_effect = [True, True, True]
        mock_as_posix.side_effect = ["/path-location/to"]

        # Act
        self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(
            self.mock_system_management_service.execute_command_params,
            [ExecuteCommandParams(["rm", "/path-location/to"])],
        )

    @patch(f"{PACKAGE_NAME}.Path.as_posix")
    @patch(f"{PACKAGE_NAME}.Path.exists")
    @patch(f"{PACKAGE_NAME}.Path.is_file")
    @patch(f"{PACKAGE_NAME}.Path.is_dir")
    def test_copy_path_removes_location_copied_to_when_it_exists_as_folder(
        self,
        mock_is_dir: MagicMock,
        mock_is_file: MagicMock,
        mock_exists: MagicMock,
        mock_as_posix: MagicMock,
    ):
        """Test copy_path removes existing destination directory before copying."""
        # Arrange
        mock_is_dir.side_effect = [True]
        mock_is_file.side_effect = [False]
        mock_exists.side_effect = [True, True, True]
        mock_as_posix.side_effect = ["/path-location/to"]

        # Act
        self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(
            self.mock_system_management_service.execute_command_params,
            [ExecuteCommandParams(["rm", "-r", "/path-location/to"])],
        )

    @patch(f"{PACKAGE_NAME}.Path.as_posix")
    @patch(f"{PACKAGE_NAME}.Path.exists")
    @patch(f"{PACKAGE_NAME}.Path.is_file")
    @patch(f"{PACKAGE_NAME}.Path.is_dir")
    def test_copy_path_with_location_removal_happy_path(
        self,
        mock_is_dir: MagicMock,
        mock_is_file: MagicMock,
        mock_exists: MagicMock,
        mock_as_posix: MagicMock,
    ):
        """Test copy_path succeeds after removing existing destination."""
        # Arrange
        mock_is_dir.side_effect = [True]
        mock_is_file.side_effect = [False]
        mock_exists.side_effect = [True, True, True]
        mock_as_posix.side_effect = ["/path-location/to"]

        # Act
        result = self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.Path.as_posix")
    @patch(f"{PACKAGE_NAME}.Path.exists")
    @patch(f"{PACKAGE_NAME}.Path.is_file")
    @patch(f"{PACKAGE_NAME}.Path.is_dir")
    def test_copy_path_remove_location_failure_results_in_copy_path_failure(
        self,
        mock_is_dir: MagicMock,
        mock_is_file: MagicMock,
        mock_exists: MagicMock,
        mock_as_posix: MagicMock,
    ):
        """Test copy_path fails when destination removal fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.mock_system_management_service.execute_command_result = fail_result
        mock_is_dir.side_effect = [True]
        mock_is_file.side_effect = [False]
        mock_exists.side_effect = [True, True, True]
        mock_as_posix.side_effect = ["/path-location/to"]

        # Act
        result = self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(result, fail_result)

    @patch(f"{PACKAGE_NAME}.Path.exists")
    def test_copy_path_executes_correct_command(self, mock_path: MagicMock):
        """Test copy_path executes correct mkdir and cp command."""
        # Arrange
        mock_path.side_effect = [True, False]

        # Act
        self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(
            self.mock_system_management_service.execute_raw_command_params,
            ["sudo mkdir -p to && sudo cp -a from to"],
        )

    @patch(f"{PACKAGE_NAME}.Path.exists")
    def test_copy_path_coppy_command_failure_results_in_copy_path_failure(
        self, mock_path: MagicMock
    ):
        """Test copy_path fails when the copy command fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.mock_system_management_service.execute_raw_command_result = fail_result
        mock_path.side_effect = [True, False]

        # Act
        result = self.service.copy_path("from", "to")

        # Assert
        self.assertEqual(result, fail_result)
