from dataclasses import dataclass

from typing import Optional

from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from .configuration_content_reader_service_contract import ConfigurationContentReaderServiceContract

@dataclass
class ReadParams:
    content: ConfigurationContent
    config: ConfigurationData
    template_path: Optional[str]

class MockConfigurationContentReaderService(ConfigurationContentReaderServiceContract):
    def __init__(self):
        self.read_params: list[ReadParams] = []
        self.read_result = OperationResult[str].succeed('')

    def read(self, content: ConfigurationContent, config: ConfigurationData, template_path: Optional[str]) -> OperationResult[str]:
        self.read_params.append(ReadParams(content, config, template_path))
        return self.read_result