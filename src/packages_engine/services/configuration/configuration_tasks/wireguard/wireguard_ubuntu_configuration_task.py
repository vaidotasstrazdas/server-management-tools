from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class WireguardUbuntuConfigurationTask(ConfigurationTask):
    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        # Necessary additional configs to be added.
        # Optional one-time server key generation (safe, idempotent)
        # "test -f /etc/wireguard/server.key || "
        # "sudo sh -c 'umask 077; wg genkey | tee /etc/wireguard/server.key | "
        # "wg pubkey | tee /etc/wireguard/server.pub >/dev/null'",
        # Do NOT start/enable wg-quick@wg0 here
        # UFW open only if UFW is active (or omit entirely)
        # "ufw status | grep -q \"Status: active\" && sudo ufw allow 51820/udp || true",
        # 'sudo systemctl enable wg-quick@wg0',
        # 'sudo systemctl start wg-quick@wg0',
        index = 2
        for client_name in data.wireguard_client_names:
            endpoint = f'10.10.0.{index}'
            index = index + 1
            set_client_wireguard_config_result = self._set_client_wireguard_config(
                client_name,
                endpoint
            )
            if not set_client_wireguard_config_result.success:
                return set_client_wireguard_config_result.as_fail()

        server_config_result = self.reader.read(
            ConfigurationContent.WIREGUARD_SERVER_CONFIG, data
        )
        if not server_config_result.success or server_config_result.data == None:
            return server_config_result.as_fail()

        write_server_config_result = self.file_system.write_text(
            '/etc/wireguard/wg0.conf', server_config_result.data)
        if not write_server_config_result.success:
            return write_server_config_result.as_fail()

        shared_config_result = self.reader.read(
            ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, data)
        if not shared_config_result.success or shared_config_result.data == None:
            return shared_config_result.as_fail()

        write_shared_config_result = self.file_system.write_text(
            f'{data.clients_data_dir}/wireguard_clients.config', shared_config_result.data)
        if not write_shared_config_result.success:
            return write_shared_config_result.as_fail()

        run_result = self.controller.run_raw_commands([
            'sudo ufw allow 51820/udp',
            'sudo systemctl enable wg-quick@wg0',
            'sudo systemctl start wg-quick@wg0',
            'sudo wg'
        ])
        if not run_result.success:
            return run_result.as_fail()

        return OperationResult[bool].succeed(True)

    def _set_client_wireguard_config(self, client_name: str, endpoint: str) -> OperationResult[bool]:
        client_private_key_path = f'/etc/wireguard/clients/{client_name}.key'
        client_public_key_path = f'/etc/wireguard/clients/{client_name}.pub'
        client_endpoint_path = f'/etc/wireguard/clients/{client_name}.endpoint'
        if self.file_system.path_exists(client_private_key_path) and self.file_system.path_exists(client_public_key_path) and self.file_system.path_exists(client_endpoint_path):
            self.notifications.info(
                f'Client "{client_name}" has WireGuard configuration already. Nothing needs to be done.'
            )
            return OperationResult[bool].succeed(True)

        run_commands_result = self.controller.run_raw_commands([
            'umask 077',
            f'wg genkey | tee {client_private_key_path} | wg pubkey > {client_public_key_path}'
        ])

        write_result = self.file_system.write_text(
            client_endpoint_path, endpoint)
        if not write_result.success:
            return write_result.as_fail()

        if not run_commands_result.success:
            return run_commands_result.as_fail()

        return OperationResult[bool].succeed(True)
