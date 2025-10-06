"""Modules necessary for the Nftables installer task implementation."""
from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService


class NftablesUbuntuInstallerTask(InstallerTask):
    """ Nftables Ubuntu installation task """

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
            'Nftables will be installed now if it is not installed.'
        )
        is_installed = self.engine.is_installed('nftables')
        if is_installed:
            self.notifications.success(
                '\tNftables is installed already. Nothing needs to be done.'
            )
            return OperationResult[bool].succeed(True)

        result = self.controller.run_raw_commands([
            'sudo DEBIAN_FRONTEND=noninteractive apt-get install '
            '-y --no-install-recommends nftables',
        ])

        if not result.success:
            self.notifications.error(
                f'Command failed. Message: {result.message}.'
            )

        return result
