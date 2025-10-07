"""Imports necessary to define the contract."""

from abc import ABC, abstractmethod
from typing import Any

from packages_engine.models import OperationResult


class FileSystemServiceContract(ABC):
    """File System Service Contract definition"""

    @abstractmethod
    def read_text(self, path_location: str) -> OperationResult[str]:
        """Reads the text from the specified path."""

    @abstractmethod
    def write_text(self, path_location: str, text: str) -> OperationResult[bool]:
        """Writes the text into the specified path."""

    @abstractmethod
    def read_json(self, path_location: str) -> OperationResult[Any]:
        """Reads the data from the specified path in any type representation."""

    @abstractmethod
    def write_json(self, path_location: str, data: Any) -> OperationResult[bool]:
        """Writes the data into the specified path in any type representation."""

    @abstractmethod
    def make_dir(self, path_location: str) -> OperationResult[bool]:
        """Creates the directory in the specified path."""

    @abstractmethod
    def chmod(self, path_location: str, chmod: int) -> OperationResult[bool]:
        """Chmods the specified path."""

    @abstractmethod
    def remove_location(self, path_location: str) -> OperationResult[bool]:
        """Removes the location specified. Can remove both files and folders. If it is a folder, removal is recursive."""

    @abstractmethod
    def path_exists(self, path_location: str) -> bool:
        """Checks if path exists. Can be both file and folder."""

    @abstractmethod
    def copy_path(self, location_from: str, location_to: str) -> OperationResult[bool]:
        """Copies path from one location to another. Can be both file and folder. If it is a folder, copies folder contents to the path specified."""
