""" "Necessary imports to implement the File System Service mock."""

from dataclasses import dataclass
from typing import Any, Dict

from packages_engine.models import OperationResult

from .file_system_service_contract import FileSystemServiceContract


@dataclass
class WriteTextParams:
    """Params of the write_text method."""

    path_location: str
    text: str


@dataclass
class WriteJsonParams:
    """Params of the write_json method."""

    path_location: str
    data: Any


@dataclass
class ChmodParams:
    """Params of the chmod method."""

    path_location: str
    chmod: int


@dataclass
class CopyPathParams:
    """Params of the copy_path method."""

    location_from: str
    location_to: str


class MockFileSystemService(FileSystemServiceContract):
    """File System Service Mock implementation."""

    def __init__(self):
        self.read_text_params: list[str] = []
        self.read_text_result = OperationResult[str].succeed("")
        self.read_text_result_map: Dict[str, OperationResult[str]] = {}
        self.write_text_params: list[WriteTextParams] = []
        self.write_text_result = OperationResult[bool].succeed(True)
        self.write_text_result_map: Dict[str, OperationResult[bool]] = {}
        self.read_json_params: list[str] = []
        self.read_json_result = OperationResult[Any].succeed({})
        self.read_json_result_map: Dict[str, OperationResult[Any]] = {}
        self.write_json_params: list[WriteJsonParams] = []
        self.write_json_result = OperationResult[bool].succeed(True)
        self.write_json_result_map: Dict[str, OperationResult[bool]] = {}
        self.make_dir_params: list[str] = []
        self.make_dir_result = OperationResult[bool].succeed(True)
        self.chmod_params: list[ChmodParams] = []
        self.chmod_result = OperationResult[bool].succeed(True)
        self.remove_location_params: list[str] = []
        self.remove_location_result = OperationResult[bool].succeed(True)
        self.remove_location_result_map: Dict[str, OperationResult[bool]] = {}
        self.path_exists_params: list[str] = []
        self.path_exists_result = True
        self.path_exists_result_map: Dict[str, bool] = {}
        self.copy_path_params: list[CopyPathParams] = []
        self.copy_path_result = OperationResult[bool].succeed(True)
        self.copy_path_result_map: Dict[str, OperationResult[bool]] = {}

    def read_text(self, path_location: str) -> OperationResult[str]:
        self.read_text_params.append(path_location)

        if path_location in self.read_text_result_map:
            return self.read_text_result_map[path_location]

        return self.read_text_result

    def write_text(self, path_location: str, text: str) -> OperationResult[bool]:
        self.write_text_params.append(WriteTextParams(path_location, text))

        if path_location in self.write_text_result_map:
            return self.write_text_result_map[path_location]

        return self.write_text_result

    def read_json(self, path_location: str) -> OperationResult[Any]:
        self.read_json_params.append(path_location)

        if path_location in self.read_json_result_map:
            return self.read_json_result_map[path_location]

        return self.read_json_result

    def write_json(self, path_location: str, data: Any) -> OperationResult[bool]:
        self.write_json_params.append(WriteJsonParams(path_location, data))

        if path_location in self.write_json_result_map:
            return self.write_json_result_map[path_location]

        return self.write_json_result

    def make_dir(self, path_location: str) -> OperationResult[bool]:
        self.make_dir_params.append(path_location)
        return self.make_dir_result

    def chmod(self, path_location: str, chmod: int) -> OperationResult[bool]:
        self.chmod_params.append(ChmodParams(path_location, chmod))
        return self.chmod_result

    def remove_location(self, path_location: str) -> OperationResult[bool]:
        self.remove_location_params.append(path_location)

        if path_location in self.remove_location_result_map:
            return self.remove_location_result_map[path_location]

        return self.remove_location_result

    def path_exists(self, path_location: str) -> bool:
        self.path_exists_params.append(path_location)

        if path_location in self.path_exists_result_map:
            return self.path_exists_result_map[path_location]

        return self.path_exists_result

    def copy_path(self, location_from: str, location_to: str) -> OperationResult[bool]:
        self.copy_path_params.append(CopyPathParams(location_from, location_to))

        copy_sequence = f"{location_from}->{location_to}"
        if copy_sequence in self.copy_path_result_map:
            return self.copy_path_result_map[copy_sequence]

        return self.copy_path_result

    def find_write_text_params(self, path_term: str) -> list[WriteTextParams]:
        """
        Fids all params of writing the text based on path search criteria.
        """
        result: list[WriteTextParams] = []
        for params in self.write_text_params:
            if path_term in params.path_location:
                result.append(params)
        return result
