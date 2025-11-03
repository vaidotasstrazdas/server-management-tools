"""Generate WireGuard peer configurations and keys on Ubuntu."""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class WireguardPeersUbuntuConfigurationTask(ConfigurationTask):
    """Generates WireGuard keys and IP assignments for server and clients."""

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        """Initialize the WireGuard peers configuration task.

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
        """Generate WireGuard private/public keys and IP addresses for all peers.

        Args:
            data: Configuration data with client names list

        Returns:
            OperationResult indicating success or failure
        """
        self.notifications.info("Preparing WireGuard server, clients configuration and keys.")

        self.notifications.info(
            "Configuring permissions for the WireGuard configurations directory."
        )
        permissions_configuration_result = self.controller.run_raw_commands(
            ["sudo install -d -m 0700 -o root -g root /etc/wireguard /etc/wireguard/clients"]
        )
        if not permissions_configuration_result.success:
            self.notifications.error(
                "Failed to configure permissions for the WireGuard configurations directory."
            )
            return permissions_configuration_result.as_fail()
        self.notifications.success(
            "Configuring permissions for the WireGuard configurations directory was successful."
        )

        self.notifications.info(
            "Will generate WireGuard configuration data files for server and clients now."
        )
        to_generate: list[tuple[str, str, str]] = [("", "server", "10.10.0.1")]
        index = 2
        for client_name in data.wireguard_client_names:
            to_generate.append(("/clients", client_name, f"10.10.0.{index}"))
            index = index + 1
        for item in to_generate:
            generate_result = self._generate_configurations(item[0], item[1], item[2])
            if not generate_result.success:
                self.notifications.error("WireGuard configuration generation failed.")
                return generate_result.as_fail()

        return OperationResult[bool].succeed(True)

    def _generate_configurations(self, directory: str, name: str, ip: str) -> OperationResult[bool]:
        config_entity = f"{directory}/{name}"
        private_key_path = f"/etc/wireguard{config_entity}.key"
        public_key_path = f"/etc/wireguard{config_entity}.pub"
        ip_path = f"/etc/wireguard{config_entity}.ip"
        if (
            self.file_system.path_exists(private_key_path)
            and self.file_system.path_exists(public_key_path)
            and self.file_system.path_exists(ip_path)
        ):
            self.notifications.info(
                f'"{config_entity}" has WireGuard configuration already. Nothing needs to be done.'
            )
            return OperationResult[bool].succeed(True)

        self.notifications.info(f'Generating configuration for the "{config_entity}".')
        gen_result = self.controller.run_raw_commands(
            [
                f"test -f /etc/wireguard{config_entity}.key || (umask 077 && wg genkey | sudo tee /etc/wireguard{config_entity}.key >/dev/null)",
                f"test -f /etc/wireguard{config_entity}.pub || (sudo cat /etc/wireguard{config_entity}.key | wg pubkey | sudo tee /etc/wireguard{config_entity}.pub >/dev/null)",
                f"sudo chmod 600 /etc/wireguard{config_entity}.key",
            ]
        )

        if not gen_result.success:
            self.notifications.error(
                f'Failed to generate the WireGuard configuration for the "{config_entity}"'
            )
            return gen_result.as_fail()

        self.notifications.success(
            f'WireGuard configuration for the "{config_entity}" has been generated successfully.'
        )

        write_result = self.file_system.write_text(ip_path, ip)
        self.notifications.info(f'Writing IP for the "{config_entity}"')
        if not write_result.success:
            self.notifications.error(f'Writing IP for the "{config_entity}" failed')
            return write_result.as_fail()
        self.notifications.success(f'Writing IP for the "{config_entity}" succeeded')

        self.notifications.info(f'Chmodding "{ip_path}".')
        chmod_result = self.controller.run_raw_commands(
            [
                f"sudo chmod 0644 {ip_path}",
            ]
        )
        if not chmod_result.success:
            self.notifications.error(f'Chmodding "{ip_path}" failed.')
            return chmod_result.as_fail()
        self.notifications.success(f'Chmodding "{ip_path}" successful.')

        return OperationResult[bool].succeed(True)
