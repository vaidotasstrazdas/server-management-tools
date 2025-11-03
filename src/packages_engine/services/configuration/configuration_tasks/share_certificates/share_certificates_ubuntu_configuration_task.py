"""Share CA certificate with VPN clients on Ubuntu."""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class ShareCertificatesUbuntuConfigurationTask(ConfigurationTask):
    """Copies CA certificate to client data directory for distribution."""

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        """Initialize the share certificates configuration task.

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
        """Copy CA certificate to client data directory.

        Args:
            data: Configuration data with client directory path

        Returns:
            OperationResult indicating success or failure
        """
        self.notifications.info("Sharing Certificates for the users.")

        self.notifications.info("Reading certificates configuration.")
        read_certificates_result = self.file_system.read_text("/etc/ssl/internal-pki/ca.crt")
        if not read_certificates_result.success or read_certificates_result.data is None:
            self.notifications.error("Reading certificates configuration failed.")
            return read_certificates_result.as_fail()

        self.notifications.success("Reading certificates configuration successful.")
        self.notifications.info("Sharing certificates configuration with clients.")
        save_config_result = self.file_system.write_text(
            f"{data.clients_data_dir}/certificate.crt", read_certificates_result.data
        )
        if not save_config_result.success:
            self.notifications.error("Sharing certificates configuration with clients failed.")
            return save_config_result.as_fail()
        self.notifications.success("Sharing certificates configuration with clients successful.")

        return OperationResult[bool].succeed(True)
