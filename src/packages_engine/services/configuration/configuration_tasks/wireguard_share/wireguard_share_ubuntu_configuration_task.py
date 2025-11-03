"""Share WireGuard client configurations on Ubuntu."""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class WireguardShareUbuntuConfigurationTask(ConfigurationTask):
    """Writes WireGuard client configuration to client data directory."""

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        """Initialize the WireGuard share configuration task.

        Args:
            reader: Service for reading configuration content
            file_system: Service for file system operations
            notifications: Service for user notifications
            controller: Service for executing system commands
        """
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Generate and save WireGuard client configuration file.

        Args:
            data: Configuration data with client directory path

        Returns:
            OperationResult indicating success or failure
        """
        self.notifications.info("Sharing WireGuard configuration for the clients.")

        self.notifications.info("Reading WireGuard shared configuration.")
        shared_config_result = self.reader.read(ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, data)
        if not shared_config_result.success or shared_config_result.data is None:
            self.notifications.error("Failed reading WireGuard shared configuration.")
            return shared_config_result.as_fail()
        self.notifications.success("Reading WireGuard shared configuration successful.")

        self.notifications.info("Writing WireGuard shared configuration.")
        write_shared_config_result = self.file_system.write_text(
            f"{data.clients_data_dir}/wg0_shared.conf", shared_config_result.data
        )
        if not write_shared_config_result.success:
            self.notifications.error("Failed writing WireGuard shared configuration.")
            return write_shared_config_result.as_fail()
        self.notifications.success("Writing WireGuard shared configuration successful.")

        return OperationResult[bool].succeed(True)
