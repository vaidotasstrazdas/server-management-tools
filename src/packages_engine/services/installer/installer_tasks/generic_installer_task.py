"""Necessary imports for the generic installer task implementation."""

import sys

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask


class GenericInstallerTask(InstallerTask):
    """Generic implementation that decides which implementation to run based on the platform."""

    def __init__(self, ubuntu: InstallerTask, windows: InstallerTask):
        self.ubuntu = ubuntu
        self.windows = windows

    def install(self) -> OperationResult[bool]:
        if sys.platform.startswith("win"):
            return self.windows.install()
        elif sys.platform.startswith("linux"):
            return self.ubuntu.install()

        return OperationResult[bool].fail(f'Not supported platform "{sys.platform}"')
