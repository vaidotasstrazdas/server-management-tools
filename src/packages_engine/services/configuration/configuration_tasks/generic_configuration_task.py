import sys

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from .configuration_task import ConfigurationTask

class GenericConfigurationTask(ConfigurationTask):
    def __init__(self, ubuntu: ConfigurationTask, windows: ConfigurationTask):
        self.ubuntu = ubuntu
        self.windows = windows

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        if sys.platform.startswith('win'):
            return self.windows.configure(data)
        elif sys.platform.startswith('linux'):
            return self.ubuntu.configure(data)
        
        return OperationResult[bool].fail(f'Not supported platform "{sys.platform}"')