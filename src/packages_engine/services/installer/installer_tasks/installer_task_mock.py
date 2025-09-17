from packages_engine.models import OperationResult

from .installer_task import InstallerTask

class MockInstallerTask(InstallerTask):
    def __init__(self):
        self.install_triggered_times = 0
        self.install_result = OperationResult[bool].succeed(True)
        
    def install(self) -> OperationResult[bool]:
        self.install_triggered_times = self.install_triggered_times + 1
        return self.install_result