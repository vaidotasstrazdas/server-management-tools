"""Imports necessary to implement the OperationResult data model."""

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class OperationResult(Generic[T]):
    """Operation Result data model implementation."""

    success: bool
    message: str = ""
    code: int = 0
    data: Optional[T] = None

    __create_key = object()

    @classmethod
    def succeed(cls, data: T):
        """Helper method that avoids full instantiation when operation succeeds. Can be used like: OperationResult[T].succeed(T value)"""
        return OperationResult[T](cls.__create_key, True, "", 0, data)

    @classmethod
    def fail(cls, message: str, code: int = 0):
        """Helper method that avoids full instantiation when operation fails. Can be used like: OperationResult[T].fail('Failure message')"""
        return OperationResult[T](cls.__create_key, False, message, code, None)

    def as_fail[U](self):
        """Can be converted into failure result from one type to another. Useful in chaining operation results."""
        return OperationResult[U](self.__create_key, False, self.message, self.code, None)

    def __init__(
        self, create_key: object, success: bool, message: str, code: int, data: Optional[T]
    ):
        if create_key is not OperationResult.__create_key:
            raise TypeError("OnlyCreatable objects must be created using OnlyCreatable.create")
        self.success = success
        self.message = message
        self.code = code
        self.data = data
