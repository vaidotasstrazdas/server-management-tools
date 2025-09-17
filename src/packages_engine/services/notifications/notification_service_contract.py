from abc import ABC, abstractmethod

class NotificationsServiceContract(ABC):
    @abstractmethod
    def info(self, text: str):
        pass

    @abstractmethod
    def error(self, text: str):
        pass

    @abstractmethod
    def success(self, text: str):
        pass

    @abstractmethod
    def warning(self, text: str):
        pass