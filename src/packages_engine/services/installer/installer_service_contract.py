from abc import ABC, abstractmethod

from packages_engine.models import OperationResult

from .installer_tasks import InstallerTask

class InstallerServiceContract(ABC):
    @abstractmethod
    def install(self, tasks: list[InstallerTask]) -> OperationResult[bool]:
        pass