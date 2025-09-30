from packages_engine.services.file_system import FileSystemService
from packages_engine.services.input_collection import InputCollectionService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.system_management_engine_locator import SystemManagementEngineLocatorService
from packages_engine.commands import SelfDeployCommand


def main():
    systemManagementEngineLocatorService = SystemManagementEngineLocatorService()
    engine = systemManagementEngineLocatorService.locate_engine()
    systemManagementService = SystemManagementService(engine)

    notifications_service = NotificationsService()

    input_collection = InputCollectionService()
    file_system = FileSystemService(systemManagementService)

    command = SelfDeployCommand(
        file_system,
        input_collection,
        notifications_service
    )
    command.execute()
