from abc import ABC, abstractmethod

from packages_engine.models import OperationResult

class InstallerTask(ABC):
    @abstractmethod
    def install(self) -> OperationResult[bool]:
        pass