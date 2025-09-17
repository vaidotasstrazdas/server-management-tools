from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

@dataclass
class OperationResult(Generic[T]):
    success: bool
    message: str = ''
    code: int = 0
    data: Optional[T] = None

    __create_key = object()

    @classmethod
    def succeed(cls, data: T):
        return OperationResult[T](cls.__create_key, True, '', 0, data)

    @classmethod
    def fail(cls, message: str, code: int = 0):
        return OperationResult[T](cls.__create_key, False, message, code, None)
    
    def as_fail[U](self):
        return OperationResult[U](self.__create_key, False, self.message, self.code, None)

    def __init__(self, create_key: object, success: bool, message: str, code: int, data: Optional[T]):
        if create_key is not OperationResult.__create_key:
            raise TypeError("OnlyCreatable objects must be created using OnlyCreatable.create")
        self.success = success
        self.message = message
        self.code = code
        self.data = data