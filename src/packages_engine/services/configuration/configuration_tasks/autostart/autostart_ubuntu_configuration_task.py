"""Ubuntu autostart service configuration.

Sets up a systemd service that runs the autostart.pyz application on boot.
"""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class AutostartUbuntuConfigurationTask(ConfigurationTask):
    """Configures autostart systemd service on Ubuntu.

    Creates and enables a systemd unit that runs autostart.pyz at boot,
    ensuring proper permissions and service activation.
    """

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        """Initialize the autostart configuration task.

        Args:
            reader: Service for reading configuration templates.
            file_system: Service for file operations.
            notifications: Service for user notifications.
            controller: Service for executing system commands.
        """
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Configure and enable the autostart systemd service.

        Verifies autostart.pyz exists, sets permissions, creates systemd unit
        from template, and enables/starts the service.

        Args:
            data: Configuration data including server data directory path.

        Returns:
            OperationResult[bool]: Success if service is configured and running.
        """
        self.notifications.info("Configuring autostart script")

        # Ensure zipapp is present and executable (self_deploy.pyz places it here)
        zipapp_path = "/usr/local/sbin/autostart.pyz"
        self.notifications.info(f"Checking {zipapp_path} presence and permissions")

        if not self.file_system.path_exists(zipapp_path):
            self.notifications.error(f"\tMissing {zipapp_path}. Run self_deploy first.")
            return OperationResult[bool].fail(f"{zipapp_path} not found")

        perm_zipapp = self.controller.run_raw_commands(
            [
                "sudo install -d -m 0755 /usr/local/sbin",
                f"sudo chown root:root {zipapp_path}",
                f"sudo chmod 0755 {zipapp_path}",
            ]
        )
        if not perm_zipapp.success:
            self.notifications.error("\tFailed to set autostart.pyz permissions")
            return perm_zipapp.as_fail()
        self.notifications.success("\tautostart.pyz permissions verified")

        # 1) Read the unit template
        autostart_data_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/autostart.service",
        )
        if not autostart_data_result.success or autostart_data_result.data is None:
            self.notifications.error("\tFailed to read autostart service template")
            return autostart_data_result.as_fail()
        self.notifications.success("\tAutostart service template read successfully")

        # 2) Write the unit file
        self.notifications.info("Saving autostart configuration in the system.")
        write_result = self.file_system.write_text(
            "/etc/systemd/system/autostart.service", autostart_data_result.data
        )
        if not write_result.success:
            self.notifications.error("\tFailed to save/overwrite autostart service")
            return write_result.as_fail()
        # Permissions on unit
        fix_unit = self.controller.run_raw_commands(
            [
                "sudo chown root:root /etc/systemd/system/autostart.service",
                "sudo chmod 0644 /etc/systemd/system/autostart.service",
            ]
        )
        if not fix_unit.success:
            self.notifications.error("\tFailed to set unit permissions")
            return fix_unit.as_fail()

        self.notifications.success("\tAutostart service configuration saved successfully")

        # 3) Enable + start the unit
        self.notifications.info("Enabling autostart service")
        run_result = self.controller.run_raw_commands(
            [
                "sudo systemctl daemon-reload",
                "sudo systemctl enable autostart.service",
                "sudo systemctl start autostart.service",
            ]
        )
        if not run_result.success:
            self.notifications.error("\tFailed to enable/start autostart service")
            return run_result.as_fail()
        self.notifications.success("\tAutostart service enabled and started")

        return OperationResult[bool].succeed(True)
