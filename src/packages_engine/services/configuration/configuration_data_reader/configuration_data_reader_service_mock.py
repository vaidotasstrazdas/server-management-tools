"""Imports for the mock implementation."""

from packages_engine.models.configuration import ConfigurationData

from .configuration_data_reader_service_contract import ConfigurationDataReaderServiceContract


class MockConfigurationDataReaderService(ConfigurationDataReaderServiceContract):
    """Mock configuration data reader service."""

    def __init__(self):
        self.read_params: list[ConfigurationData | None] = []
        self.read_result = ConfigurationData.default()
        self.read_result.server_data_dir = "srv"
        self.load_stored_triggered_times = 0
        self.load_stored_result: ConfigurationData | None = None

    def read(self, stored: ConfigurationData | None = None) -> ConfigurationData:
        self.read_params.append(stored)
        return self.read_result

    def load_stored(self) -> ConfigurationData | None:
        self.load_stored_triggered_times = self.load_stored_triggered_times + 1
        return self.load_stored_result
