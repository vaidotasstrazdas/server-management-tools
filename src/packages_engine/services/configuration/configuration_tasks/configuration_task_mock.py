from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from .configuration_task import ConfigurationTask

class MockConfigurationTask(ConfigurationTask):
    def __init__(self):
        self.configure_params: list[ConfigurationData] = []
        self.configure_result = OperationResult[bool].succeed(True)
        
    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.configure_params.append(data)
        return self.configure_result