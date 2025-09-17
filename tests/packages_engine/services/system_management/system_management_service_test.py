import unittest

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import MockSystemManagementEngineService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import ExecuteCommandParams

class TestSystemManagementService(unittest.TestCase):
    mockSystemManagementEngineService: MockSystemManagementEngineService
    service: SystemManagementService

    def setUp(self):
        self.mockSystemManagementEngineService = MockSystemManagementEngineService()
        self.service = SystemManagementService(self.mockSystemManagementEngineService)
    
    def test_is_installed_calls_check_from_engine(self):
        # Act
        self.service.is_installed('package')

        # Assert
        params = self.mockSystemManagementEngineService.is_installed_params
        self.assertEqual(params, ['package'])
    
    def test_is_installed_result_is_returned_from_engine_case_1(self):
        # Arrange
        self.mockSystemManagementEngineService.is_installed_result = True

        # Act
        result = self.service.is_installed('package')

        # Assert
        self.assertTrue(result)
    
    def test_is_installed_result_is_returned_from_engine_case_2(self):
        # Arrange
        self.mockSystemManagementEngineService.is_installed_result = False

        # Act
        result = self.service.is_installed('package')

        # Assert
        self.assertFalse(result)
    
    def test_install_calls_engine(self):
        # Act
        self.service.install('package')

        # Assert
        params = self.mockSystemManagementEngineService.install_params
        self.assertEqual(params, ['package'])
    
    def test_install_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.install_result = dto

        # Act
        result = self.service.install('package')

        # Assert
        self.assertEqual(result, dto)
    
    def test_is_running_calls_engine(self):
        # Act
        self.service.is_running('package')

        # Assert
        params = self.mockSystemManagementEngineService.is_running_params
        self.assertEqual(params, ['package'])
    
    def test_is_running_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.is_running_result = dto

        # Act
        result = self.service.is_running('package')

        # Assert
        self.assertEqual(result, dto)
    
    def test_start_calls_engine(self):
        # Act
        self.service.start('package')

        # Assert
        params = self.mockSystemManagementEngineService.start_params
        self.assertEqual(params, ['package'])
    
    def test_start_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.start_result = dto

        # Act
        result = self.service.start('package')

        # Assert
        self.assertEqual(result, dto)
    
    def test_restart_calls_engine(self):
        # Act
        self.service.restart('package')

        # Assert
        params = self.mockSystemManagementEngineService.restart_params
        self.assertEqual(params, ['package'])
    
    def test_restart_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.restart_result = dto

        # Act
        result = self.service.restart('package')

        # Assert
        self.assertEqual(result, dto)
    
    def test_execute_command_calls_engine(self):
        # Act
        self.service.execute_command(['foo', 'bar'], '/src')

        # Assert
        params = self.mockSystemManagementEngineService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(['foo', 'bar'], '/src')])
    
    def test_execute_command_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.execute_command_result = dto

        # Act
        result = self.service.execute_command(['foo', 'bar'], '/src')

        # Assert
        self.assertEqual(result, dto)
    
    def test_execute_raw_command_calls_engine(self):
        # Act
        self.service.execute_raw_command('foo bar')

        # Assert
        params = self.mockSystemManagementEngineService.execute_raw_command_params
        self.assertEqual(params, ['foo bar'])
    
    def test_execute_raw_command_returns_engine_result(self):
        # Arrange
        dto = OperationResult[bool].fail('Install not success', 9)
        self.mockSystemManagementEngineService.execute_raw_command_result = dto

        # Act
        result = self.service.execute_raw_command('foo bar')

        # Assert
        self.assertEqual(result, dto)

if __name__ == '__main__':
    unittest.main()