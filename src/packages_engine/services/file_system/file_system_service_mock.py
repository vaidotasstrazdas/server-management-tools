from dataclasses import dataclass
from typing import Dict

from packages_engine.models import OperationResult

from .file_system_service_contract import FileSystemServiceContract

@dataclass
class WriteTextParams:
    path_location: str
    text: str

@dataclass
class ChmodParams:
    path_location: str
    chmod: int

class MockFileSystemService(FileSystemServiceContract):
    def __init__(self):
        self.read_text_params: list[str] = []
        self.read_text_result = OperationResult[str].succeed('')
        self.read_text_result_map: Dict[str, OperationResult[str]] = {}
        self.write_text_params: list[WriteTextParams] = []
        self.write_text_result = OperationResult[bool].succeed(True)
        self.write_text_result_map: Dict[str, OperationResult[bool]] = {}
        self.make_dir_params: list[str] = []
        self.make_dir_result = OperationResult[bool].succeed(True)
        self.chmod_params: list[ChmodParams] = []
        self.chmod_result = OperationResult[bool].succeed(True)
        self.remove_location_params: list[str] = []
        self.remove_location_result = OperationResult[bool].succeed(True)
        self.path_exists_params: list[str] = []
        self.path_exists_result = True
        self.path_exists_result_map: Dict[str, bool] = {}

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

    def make_dir(self, path_location: str) -> OperationResult[bool]:
        self.make_dir_params.append(path_location)
        return self.make_dir_result

    def chmod(self, path_location: str, chmod: int) -> OperationResult[bool]:
        self.chmod_params.append(ChmodParams(path_location, chmod))
        return self.chmod_result

    def remove_location(self, path_location: str) -> OperationResult[bool]:
        self.remove_location_params.append(path_location)
        return self.remove_location_result

    def path_exists(self, path_location: str) -> bool:
        self.path_exists_params.append(path_location)

        if path_location in self.path_exists_result_map:
            return self.path_exists_result_map[path_location]
        
        return self.path_exists_result