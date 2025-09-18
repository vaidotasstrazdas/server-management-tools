from abc import ABC, abstractmethod

class InputCollectionServiceContract(ABC):
    @abstractmethod
    def read_str(self, title: str) -> str:
        pass

    @abstractmethod
    def read_int(self, title: str) -> int:
        pass