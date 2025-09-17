from packages_engine.models import OperationResult

from .installer_tasks import InstallerTask
from .installer_service_contract import InstallerServiceContract

class MockInstallerService(InstallerServiceContract):
    def __init__(self):
        self.install_params: list[list[InstallerTask]] = []
        self.install_result = OperationResult[bool].succeed(True)

    def install(self, tasks: list[InstallerTask]) -> OperationResult[bool]:
        self.install_params.append(tasks)
        return self.install_result