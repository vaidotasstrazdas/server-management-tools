"""Modules necessary for the stub implementation."""

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask


class PostInstallCheckWindowsInstallerTask(InstallerTask):
    """Stub Windows task."""

    def install(self) -> OperationResult[bool]:
        return OperationResult[bool].fail("Not supported")
