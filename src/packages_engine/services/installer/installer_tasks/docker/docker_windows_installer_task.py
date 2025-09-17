from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask

class DockerWindowsInstallerTask(InstallerTask):
    def install(self) -> OperationResult[bool]:
        return OperationResult[bool].fail('Not supported')