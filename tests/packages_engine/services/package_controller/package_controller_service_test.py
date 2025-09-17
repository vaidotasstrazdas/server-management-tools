import unittest

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller import PackageControllerService
from packages_engine.services.system_management.system_management_service_mock import MockSystemManagementService
from packages_engine.services.system_management.system_management_service_mock import ExecuteCommandParams

def failing_execute_raw_command_result_fn(command: str) -> OperationResult[bool]:
    if command == 'other command':
        return  OperationResult[bool].fail('failure')
    return  OperationResult[bool].succeed(True)

class TestPackageControllerService(unittest.TestCase):
    mockSystemManagementService: MockSystemManagementService
    mockNotificationsService: MockNotificationsService
    service: PackageControllerService

    def setUp(self):
        self.mockSystemManagementService = MockSystemManagementService()
        self.mockNotificationsService = MockNotificationsService()
        self.service = PackageControllerService(self.mockSystemManagementService, self.mockNotificationsService)
    
    def test_install_package_checks_for_the_installation_status(self):
        # Act
        self.service.install_package('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.is_installed_params, ['package_name'])

    def test_install_package_informs_about_package_installation_flow_when_package_is_installed_already(self):
        # Arrange
        self.mockSystemManagementService.is_installed_result = True

        # Act
        self.service.install_package('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Will try to install "package_name" if it is not installed.'},
                {'type': 'info', 'text': 'Checking if "package_name" is installed.'},
                {'type': 'success', 'text': 'Package "package_name" is installed already, nothing needs to be done.'}
            ]
        )

    def test_install_package_triggers_install_call_when_package_is_not_installed(self):
        # Arrange
        self.mockSystemManagementService.is_installed_result = False

        # Act
        self.service.install_package('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.install_params, ['package_name'])

    def test_install_package_does_not_trigger_install_call_when_package_is_installed(self):
        # Arrange
        self.mockSystemManagementService.is_installed_result = True

        # Act
        self.service.install_package('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.install_params, [])

    def test_install_package_informs_about_package_installation_flow_when_package_gets_installed_successfully(self):
        # Arrange
        self.mockSystemManagementService.is_installed_result = False
        self.mockSystemManagementService.install_result = OperationResult[bool].succeed(True)

        # Act
        self.service.install_package('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Will try to install "package_name" if it is not installed.'},
                {'type': 'info', 'text': 'Checking if "package_name" is installed.'},
                {'type': 'info', 'text': 'Package "package_name" is not installed. Will try installing it now.'},
                {'type': 'success', 'text': 'Package "package_name" was installed successfully.'}
            ]
        )

    def test_install_package_informs_about_package_installation_flow_when_package_fails_to_be_installed_successfully(self):
        # Arrange
        self.mockSystemManagementService.is_installed_result = False
        self.mockSystemManagementService.install_result = OperationResult[bool].fail('Error message text', 123)

        # Act
        self.service.install_package('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Will try to install "package_name" if it is not installed.'},
                {'type': 'info', 'text': 'Checking if "package_name" is installed.'},
                {'type': 'info', 'text': 'Package "package_name" is not installed. Will try installing it now.'},
                {'type': 'error', 'text': 'Failed to install the "package_name". Error code: 123. Error message: "Error message text".'}
            ]
        )
    
    def test_ensure_running_informs_about_flow_is_running_happy_flow(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.start_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.restart_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Running state check for the package "package_name" succeeded.', 'type': 'success'},
                {'text': 'Package "package_name" is running. Will restart it.', 'type': 'info'},
                {'text': 'Package "package_name" has been restarted successfully.', 'type': 'success'}
            ]
        )
    
    def test_ensure_running_checks_for_running_state(self):
        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.is_running_params, ['package_name'])
    
    def test_ensure_running_does_not_try_starting_package_if_it_is_running(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(True)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.start_params, [])
    
    def test_ensure_running_does_not_try_starting_package_if_running_check_fails(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].fail('fail', 1)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.start_params, [])
    
    def test_ensure_running_tries_starting_package_if_it_is_not_running(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(False)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.start_params, ['package_name'])

    def test_ensure_running_does_not_tries_restarting_package_if_it_is_running(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(True)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.restart_params, ['package_name'])
    
    def test_ensure_running_does_not_try_restarting_package_if_running_check_fails(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].fail('fail', 1)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.restart_params, [])
    
    def test_ensure_running_tries_restarting_package_if_it_is_not_running_after_starting_package(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(False)

        # Act
        self.service.ensure_running('package_name')

        # Assert
        self.assertEqual(self.mockSystemManagementService.restart_params, ['package_name'])

    def test_ensure_running_informs_about_flow_is_not_running_happy_flow(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(False)
        self.mockSystemManagementService.start_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.restart_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Running state check for the package "package_name" succeeded.', 'type': 'success'},
                {'text': 'Package "package_name" is not running. Will start it first.', 'type': 'info'},
                {'text': 'Package "package_name" has been started successfully.', 'type': 'success'},
                {'text': 'Package "package_name" has been restarted successfully.', 'type': 'success'}
            ]
        )

    def test_ensure_running_informs_about_flow_is_running_check_fails(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].fail('fail', 123)
        self.mockSystemManagementService.start_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.restart_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Check failed for the package "package_name". Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_ensure_running_informs_about_flow_start_fails(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(False)
        self.mockSystemManagementService.start_result = OperationResult[bool].fail('fail', 123)
        self.mockSystemManagementService.restart_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Running state check for the package "package_name" succeeded.', 'type': 'success'},
                {'text': 'Package "package_name" is not running. Will start it first.', 'type': 'info'},
                {'text': 'Failed to start package "package_name". Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_ensure_running_informs_about_flow_restart_fails_when_package_not_running(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(False)
        self.mockSystemManagementService.start_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.restart_result = OperationResult[bool].fail('fail', 123)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Running state check for the package "package_name" succeeded.', 'type': 'success'},
                {'text': 'Package "package_name" is not running. Will start it first.', 'type': 'info'},
                {'text': 'Package "package_name" has been started successfully.', 'type': 'success'},
                {'text': 'Failed to restart package "package_name". Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_ensure_running_informs_about_flow_restart_fails_when_package_running(self):
        # Arrange
        self.mockSystemManagementService.is_running_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.start_result = OperationResult[bool].succeed(True)
        self.mockSystemManagementService.restart_result = OperationResult[bool].fail('fail', 123)
        
        # Act
        self.service.ensure_running('package_name')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will try ensuring that package "package_name" is up and running.', 'type': 'info'},
                {'text': 'Checking if the package "package_name" is running already.', 'type': 'info'},
                {'text': 'Running state check for the package "package_name" succeeded.', 'type': 'success'},
                {'text': 'Package "package_name" is running. Will restart it.', 'type': 'info'},
                {'text': 'Failed to restart package "package_name". Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_run_command_executes_command_with_correct_parameters(self):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_command(['foo', 'bar'], '/src')

        # Assert
        params = self.mockSystemManagementService.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(['foo', 'bar'], '/src')])

    def test_run_command_informs_about_flow_when_folder_unset(self):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_command(['foo', 'bar'])

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Running command: "foo bar".', 'type': 'info'},
                {'text': 'Running command succeeded!', 'type': 'success'}
            ]
        )

    def test_run_command_informs_about_flow_when_folder_set(self):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_command(['foo', 'bar'], '/src')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Running command: "foo bar".', 'type': 'info'},
                {'text': 'Command directory selected: "/src".', 'type': 'info'},
                {'text': 'Running command succeeded!', 'type': 'success'}
            ]
        )

    def test_run_command_informs_about_flow_when_command_fails(self):
        # Arrange
        self.mockSystemManagementService.execute_command_result = OperationResult[bool].fail('fail', 123)
        
        # Act
        self.service.run_command(['foo', 'bar'], '/src')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Running command: "foo bar".', 'type': 'info'},
                {'text': 'Command directory selected: "/src".', 'type': 'info'},
                {'text': 'Running command failed. Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_run_raw_command_executes_command_with_correct_parameters(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_raw_command('foo bar')

        # Assert
        params = self.mockSystemManagementService.execute_raw_command_params
        self.assertEqual(params, ['foo bar'])

    def test_run_raw_command_informs_about_flow_when_command_succeeds(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_raw_command('foo bar')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Running command in raw mode: "foo bar".', 'type': 'info'},
                {'text': 'Running command succeeded!', 'type': 'success'}
            ]
        )

    def test_run_raw_command_informs_about_flow_when_command_fails(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].fail('fail', 123)
        
        # Act
        self.service.run_raw_command('foo bar')

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Running command in raw mode: "foo bar".', 'type': 'info'},
                {'text': 'Running command failed. Error Code: 123. Error Message: "fail".', 'type': 'error'}
            ]
        )

    def test_run_raw_commands_executes_commands_with_correct_parameters(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_raw_commands(['foo bar', 'other command'])

        # Assert
        params = self.mockSystemManagementService.execute_raw_command_params
        self.assertEqual(params, ['foo bar', 'other command'])

    def test_run_raw_commands_returns_success_when_all_commands_succeed(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].succeed(True)
        
        # Act
        result = self.service.run_raw_commands(['foo bar', 'other command'])

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_run_raw_commands_does_not_run_after_failed_first_command(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result_fn = failing_execute_raw_command_result_fn
        
        # Act
        self.service.run_raw_commands(['foo bar', 'other command', 'another one'])

        # Assert
        params = self.mockSystemManagementService.execute_raw_command_params
        self.assertEqual(params, ['foo bar', 'other command'])

    def test_run_raw_commands_returns_failure_when_first_command_fails(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result_fn = failing_execute_raw_command_result_fn
        
        # Act
        result = self.service.run_raw_commands(['foo bar', 'other command', 'another one'])

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Failed on "other command"'))

    def test_run_raw_commands_informs_about_flow_when_all_commands_succeed(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result = OperationResult[bool].succeed(True)
        
        # Act
        self.service.run_raw_commands(['foo bar', 'other command'])

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will execute command: "foo bar"', 'type': 'info'},
                {'text': '\tCommand execution successful.', 'type': 'success'},
                {'text': 'Will execute command: "other command"', 'type': 'info'},
                {'text': '\tCommand execution successful.', 'type': 'success'}
            ]
        )

    def test_run_raw_commands_informs_about_flow_when_command_fails(self):
        # Arrange
        self.mockSystemManagementService.execute_raw_command_result_fn = failing_execute_raw_command_result_fn
        
        # Act
        self.service.run_raw_commands(['foo bar', 'other command', 'another one'])

        # Assert
        params = self.mockNotificationsService.params
        self.assertEqual(
            params,
            [
                {'text': 'Will execute command: "foo bar"', 'type': 'info'},
                {'text': '\tCommand execution successful.', 'type': 'success'},
                {'text': 'Will execute command: "other command"', 'type': 'info'},
                {'text': '\tCommand execution failed.', 'type': 'error'}
            ]
        )

if __name__ == '__main__':
    unittest.main()