import unittest

from unittest.mock import patch

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import GenericInstallerTask
from packages_engine.services.installer.installer_tasks.installer_task_mock import MockInstallerTask

package_name = 'packages_engine.services.installer.installer_tasks.generic_installer_task'

class TestGenericInstallerTask(unittest.TestCase):
    mockUbuntuTask: MockInstallerTask
    mockWindowsTask: MockInstallerTask
    task: GenericInstallerTask

    def setUp(self):
        self.mockUbuntuTask = MockInstallerTask()
        self.mockWindowsTask = MockInstallerTask()
        self.task = GenericInstallerTask(self.mockUbuntuTask, self.mockWindowsTask)
    
    @patch(f'{package_name}.sys.platform', 'linux')
    def test_runs_ubuntu_task_on_ubuntu_platform(self):
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mockUbuntuTask.install_triggered_times, 1)
        self.assertEqual(self.mockWindowsTask.install_triggered_times, 0)
    
    @patch(f'{package_name}.sys.platform', 'win32')
    def test_runs_windows_task_on_windows_platform(self):
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mockUbuntuTask.install_triggered_times, 0)
        self.assertEqual(self.mockWindowsTask.install_triggered_times, 1)
    
    @patch(f'{package_name}.sys.platform', 'unknown')
    def test_runs_no_task_on_unknown_platform(self):
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mockUbuntuTask.install_triggered_times, 0)
        self.assertEqual(self.mockWindowsTask.install_triggered_times, 0)
    
    @patch(f'{package_name}.sys.platform', 'unknown')
    def test_returns_failure_on_unknown_platform(self):
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail(f'Not supported platform "unknown"'))
    
    @patch(f'{package_name}.sys.platform', 'linux')
    def test_returns_ubuntu_result_on_ubuntu_platform(self):
        # Arrange
        self.mockUbuntuTask.install_result = OperationResult[bool].succeed(True)
        self.mockWindowsTask.install_result = OperationResult[bool].fail('failed')

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.mockUbuntuTask.install_result)
    
    @patch(f'{package_name}.sys.platform', 'windows')
    def test_returns_windows_result_on_windows_platform(self):
        # Arrange
        self.mockUbuntuTask.install_result = OperationResult[bool].succeed(True)
        self.mockWindowsTask.install_result = OperationResult[bool].fail('failed')

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.mockWindowsTask.install_result)