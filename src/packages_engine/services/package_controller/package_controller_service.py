from typing import Optional

from packages_engine.models import OperationResult
from packages_engine.services.system_management import SystemManagementServiceContract
from packages_engine.services.notifications import NotificationsServiceContract

from .package_controller_service_contract import PackageControllerServiceContract

class PackageControllerService(PackageControllerServiceContract):
    systemManagementService: SystemManagementServiceContract
    notificationsService: NotificationsServiceContract

    def __init__(self, systemManagementService: SystemManagementServiceContract, notificationsService: NotificationsServiceContract):
        self.systemManagementService = systemManagementService
        self.notificationsService = notificationsService

    def install_package(self, package: str):
        self.notificationsService.info(f'Will try to install "{package}" if it is not installed.')
        self.notificationsService.info(f'Checking if "{package}" is installed.')
        is_installed = self.systemManagementService.is_installed(package)
        if not is_installed:
            self.notificationsService.info(f'Package "{package}" is not installed. Will try installing it now.')
            install_result = self.systemManagementService.install(package)
            if install_result.success:
                self.notificationsService.success(f'Package "{package}" was installed successfully.')
            else:
                self.notificationsService.error(f'Failed to install the "{package}". Error code: {install_result.code}. Error message: "{install_result.message}".')
        else:
            self.notificationsService.success(f'Package "{package}" is installed already, nothing needs to be done.')
    
    def ensure_running(self, package: str):
        self.notificationsService.info(f'Will try ensuring that package "{package}" is up and running.')
        self.notificationsService.info(f'Checking if the package "{package}" is running already.')
        is_running_result = self.systemManagementService.is_running(package)
        if is_running_result.success == True:
            self.notificationsService.success(f'Running state check for the package "{package}" succeeded.')
            is_running = is_running_result.data
            if is_running == True:
                self.notificationsService.info(f'Package "{package}" is running. Will restart it.')
            else:
                self.notificationsService.info(f'Package "{package}" is not running. Will start it first.')

                start_result = self.systemManagementService.start(package)
                if start_result.success == True:
                    self.notificationsService.success(f'Package "{package}" has been started successfully.')
                else:
                    self.notificationsService.error(f'Failed to start package "{package}". Error Code: {start_result.code}. Error Message: "{start_result.message}".')
                    return
            
            restart_result = self.systemManagementService.restart(package)
            if restart_result.success:
                self.notificationsService.success(f'Package "{package}" has been restarted successfully.')
            else:
                self.notificationsService.error(f'Failed to restart package "{package}". Error Code: {restart_result.code}. Error Message: "{restart_result.message}".')
        else:
            self.notificationsService.error(f'Check failed for the package "{package}". Error Code: {is_running_result.code}. Error Message: "{is_running_result.message}".')

    def run_command(self, command: list[str], directory: Optional[str] = None):
        command_str = str.join(' ', command)
        self.notificationsService.info(f'Running command: "{command_str}".')
        if directory != None:
            self.notificationsService.info(f'Command directory selected: "{directory}".')
        
        result = self.systemManagementService.execute_command(command, directory)
        if result.success == True:
            self.notificationsService.success('Running command succeeded!')
        else:
            self.notificationsService.error(f'Running command failed. Error Code: {result.code}. Error Message: "{result.message}".')
    
    def run_raw_command(self, command: str):
        self.notificationsService.info(f'Running command in raw mode: "{command}".')
        result = self.systemManagementService.execute_raw_command(command)
        if result.success == True:
            self.notificationsService.success('Running command succeeded!')
        else:
            self.notificationsService.error(f'Running command failed. Error Code: {result.code}. Error Message: "{result.message}".')
    
    def run_raw_commands(self, commands: list[str]) -> OperationResult[bool]:
        for command in commands:
            self.notificationsService.info(f'Will execute command: "{command}"')
            execute_raw_command_result = self.systemManagementService.execute_raw_command(command)
            if not execute_raw_command_result.success:
                self.notificationsService.error(f'\tCommand execution failed.')
                return OperationResult[bool].fail(f'Failed on "{command}"')
            else:
                self.notificationsService.success(f'\tCommand execution successful.')
        return OperationResult[bool].succeed(True)