from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService

class WireguardUbuntuInstallerTask(InstallerTask):
    def __init__(
            self,
            notifications: NotificationsServiceContract,
            engine: SystemManagementEngineService,
            controller: PackageControllerServiceContract):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info('WireGuard will be installed now if it is not installed.')
        is_installed = self.engine.is_installed('wireguard')
        if is_installed:
            self.notifications.success('\tWireGuard is installed already. Nothing needs to be done.')
            return OperationResult[bool].succeed(True)
        
        result = self.controller.run_raw_commands([
            'sudo apt update',
            'sudo apt install wireguard -y',
            'sudo systemctl enable wg-quick@wg0',
            'sudo systemctl start wg-quick@wg0',
            'sudo ufw allow 51820/udp',
            'sudo mkdir -p /etc/wireguard',
            'sudo chmod 700 /etc/wireguard',
            'sudo mkdir -p /etc/wireguard/clients',
            'sudo chmod 700 /etc/wireguard/clients',
            'umask 077',
            'sudo wg genkey | sudo tee /etc/wireguard/server.key | wg pubkey | sudo tee /etc/wireguard/server.pub'
        ])

        return result