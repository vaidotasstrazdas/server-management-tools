from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class WireguardUbuntuConfigurationTask(ConfigurationTask):
    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info("Will Configure WireGuard now.")
        self.notifications.info("Reading WireGuard configuration.")
        server_config_result = self.reader.read(ConfigurationContent.WIREGUARD_SERVER_CONFIG, data)
        if not server_config_result.success or server_config_result.data is None:
            self.notifications.error("Failed reading WireGuard configuration.")
            return server_config_result.as_fail()
        self.notifications.success("Reading WireGuard configuration successful.")

        # Comment this out later
        self.notifications.info(f"WireGuard configuration is below:\n{server_config_result.data}")

        self.notifications.info("Writing WireGuard configuration.")
        write_server_config_result = self.file_system.write_text(
            "/etc/wireguard/wg0.conf", server_config_result.data
        )
        if not write_server_config_result.success:
            self.notifications.error("Failed writing WireGuard configuration.")
            return write_server_config_result.as_fail()
        self.notifications.success("Writing WireGuard configuration successful.")

        self.notifications.info("Fixing WireGuard configuration file permissions.")
        fixperm = self.controller.run_raw_commands(["sudo chmod 600 /etc/wireguard/wg0.conf"])
        if not fixperm.success:
            self.notifications.error("Fixing WireGuard configuration file permissions failed.")
            return fixperm.as_fail()
        self.notifications.success("Fixing WireGuard configuration file permissions successful.")

        self.notifications.info("Starting wg0.")
        up_result = self.controller.run_raw_commands(
            [
                "sudo bash -lc 'wg-quick strip wg0 > /run/wg0.conf && wg syncconf wg0 /run/wg0.conf || wg-quick up wg0'",
                "sudo systemctl enable wg-quick@wg0",
            ]
        )
        if not up_result.success:
            self.notifications.error("Failed to start wg-quick@wg0.")
            return up_result.as_fail()

        self.notifications.success("WireGuard configured and wg0 is up.")
        return OperationResult[bool].succeed(True)
