"""Necessary imports for the configure command."""

from packages_engine.services.configuration import ConfigurationDataReaderServiceContract
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask


class ConfigureCommand:
    """Configure command implementation."""

    def __init__(
        self,
        config_data_reader: ConfigurationDataReaderServiceContract,
        tasks: list[ConfigurationTask],
    ):
        self.config_data_reader = config_data_reader
        self.tasks = tasks

    def execute(self):
        """Method that executes all the configured configuration tasks."""
        stored_config_data = self.config_data_reader.load_stored()
        config_data = self.config_data_reader.read(stored_config_data)
        for task in self.tasks:
            configure_result = task.configure(config_data)
            print("config result", configure_result.success)
            if not configure_result.success:
                return
