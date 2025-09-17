from packages_engine.commands.autostart_command import AutostartCommand
from packages_engine.services.package_controller import PackageControllerService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.system_management_engine_locator import SystemManagementEngineLocatorService

def main():
    systemManagementEngineLocatorService = SystemManagementEngineLocatorService()
    engine = systemManagementEngineLocatorService.locate_engine()
    systemManagementService = SystemManagementService(engine)

    notificationsService = NotificationsService()

    controller = PackageControllerService(systemManagementService, notificationsService)

    command = AutostartCommand(controller)
    
    command.execute()