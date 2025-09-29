from abc import ABC, abstractmethod

from packages_engine.models import OperationResult

class FileSystemServiceContract(ABC):
    @abstractmethod
    def read_text(self, path_location: str) -> OperationResult[str]:
        pass

    @abstractmethod
    def write_text(self, path_location: str, text: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def make_dir(self, path_location: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def chmod(self, path_location: str, chmod: int) -> OperationResult[bool]:
        pass

    @abstractmethod
    def remove_location(self, path_location: str) -> OperationResult[bool]:
        pass

    @abstractmethod
    def path_exists(self, path_location: str) -> bool:
        pass