"""Modules necessary for the Docker installer task implementation."""

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService


class DockerUbuntuInstallerTask(InstallerTask):
    """Docker Linux Ubuntu installation task implementation."""

    def __init__(
        self,
        notifications: NotificationsServiceContract,
        engine: SystemManagementEngineService,
        controller: PackageControllerServiceContract,
    ):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info("Docker will be installed now if it is not installed.")
        is_installed = self.engine.is_installed("docker-ce")
        if is_installed:
            self.notifications.success("\tDocker is installed already. Nothing needs to be done.")
            return OperationResult[bool].succeed(True)

        result = self.controller.run_raw_commands(
            [
                # 0) Remove conflicting packages (safe to run even if none present)
                "for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker "
                "containerd runc; do sudo apt-get -y remove $pkg >/dev/null 2>&1 || true; done",
                # 1) Keyring dir + official key (per docs)
                "sudo install -m 0755 -d /etc/apt/keyrings",
                "test -f /etc/apt/keyrings/docker.asc || sudo curl -fsSL "
                "https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
                "sudo chmod a+r /etc/apt/keyrings/docker.asc",
                # 2) Repo line (idempotent write)
                "grep -qs '^deb .*download.docker.com/linux/ubuntu' "
                "/etc/apt/sources.list.d/docker.list || "
                'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] '
                "https://download.docker.com/linux/ubuntu "
                '$(. /etc/os-release && echo \\"${UBUNTU_CODENAME:-$VERSION_CODENAME}\\") stable" | '
                "sudo tee /etc/apt/sources.list.d/docker.list >/dev/null",
                # 3) Update indexes NOW that the repo exists
                "sudo DEBIAN_FRONTEND=noninteractive apt-get update",
                # 4) Install Docker Engine + friends (no recommends keeps it lean)
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "
                "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
            ]
        )

        if not result.success:
            self.notifications.error(f"Command failed. Message: {result.message}.")

        return result
