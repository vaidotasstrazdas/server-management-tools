from packages_engine.models import OperationResult

from .installer_tasks import InstallerTask
from .installer_service_contract import InstallerServiceContract

class InstallerService(InstallerServiceContract):
    def install(self, tasks: list[InstallerTask]) -> OperationResult[bool]:
        for task in tasks:
            result = task.install()
            if not result.success:
                return result.as_fail()
        
        return OperationResult[bool].succeed(True)