from pathlib import Path

from typing import Any
import unittest
from unittest.mock import call, MagicMock, create_autospec, patch

from packages_engine.models import OperationResult
from packages_engine.services.system_management.system_management_service_mock import MockSystemManagementService
from packages_engine.services.system_management.system_management_service_mock import ExecuteCommandParams
from packages_engine.services.file_system import FileSystemService

package_name = 'packages_engine.services.file_system.file_system_service'

class TestFileSystemServiceSpecData:
    def mock_read_text(self, exists: bool, is_file: bool, result: str, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.read_text.return_value = result
        mock_path.return_value = path_instance
        return path_instance

    def mock_write_text(self, exists: bool, is_file: bool, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.write_text.return_value = 0
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = '/absolute-path.txt'
        mock_path.return_value = path_instance
        return path_instance

    def mock_make_dir(self, exists: bool, is_file: bool, is_dir: bool, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.is_dir.return_value = is_dir
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = '/absolute-path'
        mock_path.return_value = path_instance
        return path_instance

    def mock_chmod(self, exists: bool, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = '/absolute-path'
        mock_path.return_value = path_instance
        return path_instance

    def mock_remove_location(self, exists: bool, is_file: bool, is_dir: bool, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        path_instance.is_file.return_value = is_file
        path_instance.is_dir.return_value = is_dir
        path_instance.absolute.return_value = path_instance
        path_instance.as_posix.return_value = '/absolute-path'
        mock_path.return_value = path_instance
        return path_instance

    def mock_path_exists(self, exists: bool, mock_path: MagicMock) -> Any:
        path_instance = create_autospec(Path, instance=True)
        path_instance.exists.return_value = exists
        mock_path.return_value = path_instance
        return path_instance

class TestFileSystemService(unittest.TestCase):
    mockSystemManagementService: MockSystemManagementService
    service: FileSystemService
    data: TestFileSystemServiceSpecData

    def setUp(self):
        self.mockSystemManagementService = MockSystemManagementService()
        self.service = FileSystemService(self.mockSystemManagementService)
        self.data = TestFileSystemServiceSpecData()
    
    @patch(f'{package_name}.Path')
    def test_read_text_happy_path(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_read_text(
            exists=True,
            is_file=True,
            result='text content',
            mock_path=mock_path
        )

        # Act
        result = self.service.read_text('file.txt')

        # Assert
        self.assertEqual(result, OperationResult[str].succeed('text content'))

    @patch(f'{package_name}.Path')
    def test_read_text_happy_path_make_correct_calls_on_file_system(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_read_text(
            exists=True,
            is_file=True,
            result='text content',
            mock_path=mock_path
        )

        # Act
        self.service.read_text('file.txt')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('file.txt'),
                call().exists(),
                call().is_file(),
                call('file.txt'),
                call().read_text(encoding='utf-8')
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_read_text_fails_when_file_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_read_text(
            exists=False,
            is_file=True,
            result='text content',
            mock_path=mock_path
        )

        # Act
        result = self.service.read_text('file.txt')

        # Assert
        self.assertEqual(result, OperationResult[str].fail('Path file.txt does not exist'))

    @patch(f'{package_name}.Path')
    def test_read_text_fails_when_location_is_not_file(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_read_text(
            exists=True,
            is_file=False,
            result='text content',
            mock_path=mock_path
        )

        # Act
        result = self.service.read_text('file.txt')

        # Assert
        self.assertEqual(result, OperationResult[str].fail('Path file.txt is not a file'))

    @patch(f'{package_name}.Path')
    def test_write_text_happy_path(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_write_text(
            exists=True,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.write_text('file.txt', 'content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_write_text_happy_path_make_correct_calls_on_file_system(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_write_text(
            exists=True,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        self.service.write_text('file.txt', 'content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('file.txt'),
                call().exists(),
                call().is_file(),
                call().exists(),
                call().write_text('content', encoding='utf-8')
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_write_text_fails_when_location_is_not_file(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_read_text(
            exists=True,
            is_file=False,
            result='text content',
            mock_path=mock_path
        )

        # Act
        result = self.service.write_text('file.txt', 'content')

        # Assert
        self.assertEqual(result, OperationResult[str].fail('Path file.txt is not a file'))
    
    @patch(f'{package_name}.Path')
    def test_write_text_creates_file_if_it_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_write_text(
            exists=False,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        self.service.write_text('file.txt', 'content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["touch", '/absolute-path.txt'])])

    @patch(f'{package_name}.Path')
    def test_write_text_does_not_create_file_if_it_exists(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_write_text(
            exists=True,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        self.service.write_text('file.txt', 'content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [])

    @patch(f'{package_name}.Path')
    def test_write_text_returns_success_when_not_existing_file_is_created_successfully(self, mock_path: MagicMock):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].succeed(True)
        self.data.mock_write_text(
            exists=False,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.write_text('file.txt', 'content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_write_text_returns_failure_when_not_existing_filecreation_command_fails(self, mock_path: MagicMock):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].fail('failure')
        self.data.mock_write_text(
            exists=False,
            is_file=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.write_text('file.txt', 'content')

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('failure'))

    @patch(f'{package_name}.Path')
    def test_make_dir_happy_path_when_dir_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=False,
            is_file=True,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.make_dir('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_make_dir_happy_path_when_dir_exists(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.make_dir('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_make_dir_makes_correct_calls_on_file_system_when_dir_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=False,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.make_dir('./content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_make_dir_makes_correct_calls_on_file_system_when_dir_exists(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.make_dir('./content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
                call().is_file(),
                call().is_dir(),
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_make_dir_executes_command_when_dir_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=False,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.make_dir('./content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["mkdir", "-p", "/absolute-path"])])

    @patch(f'{package_name}.Path')
    def test_make_dir_does_not_execute_command_when_dir_exists(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.make_dir('./content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [])

    @patch(f'{package_name}.Path')
    def test_make_dir_returns_fail_when_existing_path_is_file(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.make_dir('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Path ./content is file, so can not make the directory out of it.'))

    @patch(f'{package_name}.Path')
    def test_make_dir_returns_fail_when_existing_path_is_not_directory(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_make_dir(
            exists=True,
            is_file=False,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.make_dir('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Path ./content is not a file and not a directory.'))

    @patch(f'{package_name}.Path')
    def test_make_dir_returns_fail_when_creation_command_fails(self, mock_path: MagicMock):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].fail('failure')
        self.data.mock_make_dir(
            exists=False,
            is_file=False,
            is_dir=False,
            mock_path=mock_path
        )

        # Actx
        result = self.service.make_dir('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('failure'))

    @patch(f'{package_name}.Path')
    def test_chmod_happy_path(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_chmod(
            exists=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.chmod('./content', 777)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_chmod_happy_path_makes_correct_calls_on_file_system(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_chmod(
            exists=True,
            mock_path=mock_path
        )

        # Act
        self.service.chmod('./content', 777)

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_chmod_executes_correct_command(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_chmod(
            exists=True,
            mock_path=mock_path
        )

        # Act
        self.service.chmod('./content', 777)

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["chmod", "777", "/absolute-path"])])

    @patch(f'{package_name}.Path')
    def test_chmod_does_not_execute_command_on_not_existing_path(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_chmod(
            exists=False,
            mock_path=mock_path
        )

        # Act
        self.service.chmod('./content', 777)

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [])

    @patch(f'{package_name}.Path')
    def test_chmod_returns_failure_when_path_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_chmod(
            exists=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.chmod('./content', 777)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail(f'Path ./content does not exist.'))

    @patch(f'{package_name}.Path')
    def test_chmod_returns_success_when_command_succeeds(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_chmod(
            exists=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.chmod('./content', 777)

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_returns_failure_when_command_fails(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].fail('Failure')
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_chmod(
            exists=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.chmod('./content', 777)

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_happy_path_when_item_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=False,
            is_file=False,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_makes_correct_calls_when_item_does_not_exist(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=False,
            is_file=False,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        self.service.remove_location('./content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_happy_path_when_item_exists_as_file(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_makes_correct_calls_when_item_exists_as_file(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        self.service.remove_location('./content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
                call().absolute(),
                call().as_posix(),
                call().is_file()
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_happy_path_when_item_exists_as_folder(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_makes_correct_calls_when_item_exists_as_folder(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.remove_location('./content')

        # Assert
        mock_path.assert_has_calls(
            calls=[
                call('./content'),
                call().exists(),
                call().absolute(),
                call().as_posix(),
                call().is_file(),
                call().is_dir()
            ],
            any_order=False
        )

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_fails_when_location_is_neither_file_nor_dir(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, OperationResult[bool].fail(f'Location ./content is neither file nor directory.'))

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_file_succeeds_when_command_succeeds(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_remove_location(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_file_fails_when_command_fails(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].fail('failure')
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_remove_location(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_file_executes_correct_command(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=True,
            is_dir=False,
            mock_path=mock_path
        )

        # Act
        self.service.remove_location('./content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["rm", "/absolute-path"])])

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_folder_succeeds_when_command_succeeds(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_folder_fails_when_command_fails(self, mock_path: MagicMock):
        # Arrange
        command_result = OperationResult[bool].fail('failure')
        self.mockSystemManagementService.execute_command_result = command_result
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.remove_location('./content')

        # Assert
        self.assertEqual(result, command_result)

    @patch(f'{package_name}.Path')
    def test_chmod_remove_location_folder_executes_correct_command(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_remove_location(
            exists=True,
            is_file=False,
            is_dir=True,
            mock_path=mock_path
        )

        # Act
        self.service.remove_location('./content')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["rm", "-r", "/absolute-path"])])

    @patch(f'{package_name}.Path')
    def test_path_exists_case_1(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_path_exists(
            exists=True,
            mock_path=mock_path
        )

        # Act
        result = self.service.path_exists('./content')

        # Assert
        self.assertTrue(result)

    @patch(f'{package_name}.Path')
    def test_path_exists_case_2(self, mock_path: MagicMock):
        # Arrange
        self.data.mock_path_exists(
            exists=False,
            mock_path=mock_path
        )

        # Act
        result = self.service.path_exists('./content')

        # Assert
        self.assertFalse(result)