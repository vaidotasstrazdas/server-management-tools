from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

from .input_collection_service_contract import InputCollectionServiceContract

T = TypeVar('T')

@dataclass
class ReadParams(Generic[T]):
    title: str
    default_value: Optional[T] = None
    call_order: int = 0

class MockInputCollectionService(InputCollectionServiceContract):
    def __init__(self):
        self.read_str_params: list[ReadParams[str]] = []
        self.read_str_result = ''
        self.read_str_result_fn: Optional[Callable[[int, str, Optional[str]], str]] = None
        self.read_int_params: list[ReadParams[int]] = []
        self.read_int_result = 0
        self.read_int_result_fn: Optional[Callable[[int, str, Optional[int]], int]] = None
        self.call_order = 0
        
    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        self.call_order = self.call_order + 1
        self.read_str_params.append(ReadParams(title, default_value, self.call_order))
        if self.read_str_result_fn != None:
            return self.read_str_result_fn(self.call_order, title, default_value)
        return self.read_str_result

    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        self.call_order = self.call_order + 1
        self.read_int_params.append(ReadParams(title, default_value, self.call_order))
        if self.read_int_result_fn != None:
            return self.read_int_result_fn(self.call_order, title, default_value)
        return self.read_int_result