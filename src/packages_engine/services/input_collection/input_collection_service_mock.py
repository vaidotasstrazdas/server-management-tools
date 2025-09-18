from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from .input_collection_service_contract import InputCollectionServiceContract

T = TypeVar('T')

@dataclass
class ReadParams(Generic[T]):
    title: str
    default_value: Optional[T] = None

class MockInputCollectionServiceContract(InputCollectionServiceContract):
    def __init__(self):
        self.read_str_params: list[ReadParams[str]] = []
        self.read_str_result = ''
        self.read_int_params: list[ReadParams[int]] = []
        self.read_int_result = 0
        
    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        self.read_str_params.append(ReadParams(title, default_value))
        return self.read_str_result

    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        self.read_int_params.append(ReadParams(title, default_value))
        return self.read_int_result