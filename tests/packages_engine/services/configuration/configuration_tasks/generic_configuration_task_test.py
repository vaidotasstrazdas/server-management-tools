import unittest

from unittest.mock import patch

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult
from packages_engine.services.configuration.configuration_tasks import GenericConfigurationTask
from packages_engine.services.configuration.configuration_tasks.configuration_task_mock import MockConfigurationTask

package_name = 'packages_engine.services.configuration.configuration_tasks.generic_configuration_task'

class TestGenericConfigurationTask(unittest.TestCase):
    mockUbuntuTask: MockConfigurationTask
    mockWindowsTask: MockConfigurationTask
    configData: ConfigurationData
    task: GenericConfigurationTask

    def setUp(self):
        self.mockUbuntuTask = MockConfigurationTask()
        self.mockWindowsTask = MockConfigurationTask()
        self.configData = ConfigurationData.default()
        self.task = GenericConfigurationTask(self.mockUbuntuTask, self.mockWindowsTask)
    
    @patch(f'{package_name}.sys.platform', 'linux')
    def test_runs_ubuntu_task_on_ubuntu_platform(self):
        # Act
        self.task.configure(self.configData)

        # Assert
        self.assertEqual(self.mockUbuntuTask.configure_params, [self.configData])
        self.assertEqual(self.mockWindowsTask.configure_params, [])
    
    @patch(f'{package_name}.sys.platform', 'win32')
    def test_runs_windows_task_on_windows_platform(self):
        # Act
        self.task.configure(self.configData)

        # Assert
        self.assertEqual(self.mockUbuntuTask.configure_params, [])
        self.assertEqual(self.mockWindowsTask.configure_params, [self.configData])
    
    @patch(f'{package_name}.sys.platform', 'unknown')
    def test_runs_no_task_on_unknown_platform(self):
        # Act
        self.task.configure(self.configData)

        # Assert
        self.assertEqual(self.mockUbuntuTask.configure_params, [])
        self.assertEqual(self.mockWindowsTask.configure_params, [])
    
    @patch(f'{package_name}.sys.platform', 'unknown')
    def test_returns_failure_on_unknown_platform(self):
        # Act
        result = self.task.configure(self.configData)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail(f'Not supported platform "unknown"'))
    
    @patch(f'{package_name}.sys.platform', 'linux')
    def test_returns_ubuntu_result_on_ubuntu_platform(self):
        # Arrange
        self.mockUbuntuTask.configure_result = OperationResult[bool].succeed(True)
        self.mockWindowsTask.configure_result = OperationResult[bool].fail('failed')

        # Act
        result = self.task.configure(self.configData)

        # Assert
        self.assertEqual(result, self.mockUbuntuTask.configure_result)
    
    @patch(f'{package_name}.sys.platform', 'windows')
    def test_returns_windows_result_on_windows_platform(self):
        # Arrange
        self.mockUbuntuTask.configure_result = OperationResult[bool].succeed(True)
        self.mockWindowsTask.configure_result = OperationResult[bool].fail('failed')

        # Act
        result = self.task.configure(self.configData)

        # Assert
        self.assertEqual(result, self.mockWindowsTask.configure_result)