"""Modules necessary for the Nginx installer task implementation."""
from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService


class NginxUbuntuInstallerTask(InstallerTask):
    """Nginx Linux Ubuntu server task implementation."""

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
            'Nginx will be installed now if it is not installed.'
        )

        is_installed = self.engine.is_installed(
            'nginx'
        ) or self.engine.is_installed('nginx-core')
        if is_installed:
            self.notifications.success(
                '\tNginx is installed already. Nothing needs to be done.'
            )
            return OperationResult[bool].succeed(True)

        result = self.controller.run_raw_commands([
            # Install nginx + stream module, lean install
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install "
            "-y --no-install-recommends nginx libnginx-mod-stream",

            # Remove only the default-enabled site (symlink). Keep sites-available intact.
            "sudo rm -f /etc/nginx/sites-enabled/default",

            # Keep Nginx stopped until the config task writes proper configs and validates them.
            # This keeps ports 80/443 closed from nginx side (your firewall may still block).
            "sudo systemctl disable --now nginx || true",
        ])

        if not result.success:
            self.notifications.error(
                f'Command failed. Message: {result.message}.'
            )

        return result
