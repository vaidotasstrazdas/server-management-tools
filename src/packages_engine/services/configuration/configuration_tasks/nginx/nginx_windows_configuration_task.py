from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask

class NginxWindowsConfigurationTask(ConfigurationTask):
    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        return OperationResult[bool].fail('Not supported')