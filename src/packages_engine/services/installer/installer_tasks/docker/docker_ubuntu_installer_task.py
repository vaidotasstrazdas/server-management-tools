from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService

class DockerUbuntuInstallerTask(InstallerTask):
    def __init__(
            self,
            notifications: NotificationsServiceContract,
            engine: SystemManagementEngineService,
            controller: PackageControllerServiceContract):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info('Docker will be installed now if it is not installed.')
        is_installed = self.engine.is_installed('docker-ce')
        if is_installed:
            self.notifications.success('\tDocker is installed already. Nothing needs to be done.')
            return OperationResult[bool].succeed(True)
        
        result = self.controller.run_raw_commands([
            'sudo apt update',
            'sudo apt install -y ca-certificates curl gnupg',
            'sudo install -m 0755 -d /etc/apt/keyrings',
            'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null',
            'sudo apt update',
            'sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin',
            'sudo systemctl enable --now docker',
        ])

        return result