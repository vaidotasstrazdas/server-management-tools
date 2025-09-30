from packages_engine.models.configuration import ConfigurationData

from .configuration_data_reader_service_contract import ConfigurationDataReaderServiceContract


class MockConfigurationDataReaderService(ConfigurationDataReaderServiceContract):
    def __init__(self):
        self.read_triggered_times = 0
        self.read_result = ConfigurationData.default()
        self.read_result.server_data_dir = 'srv'

    def read(self) -> ConfigurationData:
        self.read_triggered_times = self.read_triggered_times + 1
        return self.read_result
