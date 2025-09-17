import sys

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask

class GenericInstallerTask(InstallerTask):
    def __init__(self, ubuntu: InstallerTask, windows: InstallerTask):
        self.ubuntu = ubuntu
        self.windows = windows

    def install(self) -> OperationResult[bool]:
        if sys.platform.startswith('win'):
            return self.windows.install()
        elif sys.platform.startswith('linux'):
            return self.ubuntu.install()
        
        return OperationResult[bool].fail(f'Not supported platform "{sys.platform}"')