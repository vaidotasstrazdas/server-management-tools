from packages_engine.services.configuration import ConfigurationDataReaderServiceContract
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask


class ConfigureCommand:
    def __init__(self, config_data_reader: ConfigurationDataReaderServiceContract, tasks: list[ConfigurationTask]):
        self.config_data_reader = config_data_reader
        self.tasks = tasks

    def execute(self):
        config_data = self.config_data_reader.read()
        for task in self.tasks:
            configure_result = task.configure(config_data)
            print('config result', configure_result.success)
            if not configure_result.success:
                return
