from abc import ABC, abstractmethod

from typing import Optional

class InputCollectionServiceContract(ABC):
    @abstractmethod
    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        pass