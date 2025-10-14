"""Modules necessary for the Setup installer task implementation."""

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class SetupUbuntuInstallerTask(InstallerTask):
    """Setup Installer Task implementation on Linux Ubuntu Server platform"""

    def __init__(
        self,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        self.notifications = notifications
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info(
            "Installation setup task will be executed before installing other dependencies"
        )

        result = self.controller.run_raw_commands(
            [
                "sudo DEBIAN_FRONTEND=noninteractive apt-get update",
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl gnupg lsb-release jq",
            ]
        )

        if not result.success:
            self.notifications.error(f"Command failed. Message: {result.message}.")

        return result
