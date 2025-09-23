from dataclasses import dataclass

from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult
from .content_reader import ContentReader

@dataclass
class ReadParams:
    config: ConfigurationData
    path: Optional[str] = None

class MockContentReader(ContentReader):
    def __init__(self):
        self.read_params: list[ReadParams] = []
        self.read_result = OperationResult[str].succeed('')

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        self.read_params.append(ReadParams(config, path))
        return self.read_result