"""Necessary imports to configure the self deployment tool."""

from packages_engine.commands import SelfDeployCommand
from packages_engine.services.file_system import FileSystemService
from packages_engine.services.input_collection import InputCollectionService
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.system_management_engine_locator import (
    SystemManagementEngineLocatorService,
)


def main():
    """Entry point."""
    system_management_engine_locator_service = SystemManagementEngineLocatorService()
    engine = system_management_engine_locator_service.locate_engine()
    system_management_service = SystemManagementService(engine)

    notifications_service = NotificationsService()

    input_collection = InputCollectionService(notifications_service)
    file_system = FileSystemService(system_management_service)

    command = SelfDeployCommand(file_system, input_collection, notifications_service)
    command.execute()
