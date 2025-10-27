from packages_engine.commands import AutostartCommand
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.package_controller import PackageControllerService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.system_management_engine_locator import (
    SystemManagementEngineLocatorService,
)


def main():
    system_management_engine_locator_service = SystemManagementEngineLocatorService()
    engine = system_management_engine_locator_service.locate_engine()
    system_management_service = SystemManagementService(engine)

    notifications_service = NotificationsService()

    controller = PackageControllerService(system_management_service, notifications_service)

    command = AutostartCommand(controller)

    command.execute()
