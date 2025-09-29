from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService


class NginxUbuntuInstallerTask(InstallerTask):
    def __init__(
            self,
            notifications: NotificationsServiceContract,
            engine: SystemManagementEngineService,
            controller: PackageControllerServiceContract):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info(
            'Nginx will be installed now if it is not installed.')
        is_installed = self.engine.is_installed('nginx')
        if is_installed:
            self.notifications.success(
                '\tNginx is installed already. Nothing needs to be done.')
            return OperationResult[bool].succeed(True)

        result = self.controller.run_raw_commands([
            'sudo apt update',
            'sudo apt install nginx',
            'sudo rm /etc/nginx/sites-available',
            'sudo rm /etc/nginx/sites-enabled/default',
            'sudo rm -r /var/www',
            'sudo apt update',
            'sudo apt install -y libnginx-mod-stream'
        ])

        return result
