"""Imports to implement configure command tests"""

import unittest

from packages_engine.commands import ConfigureCommand
from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_data_reader.configuration_data_reader_service_mock import (
    MockConfigurationDataReaderService,
)
from packages_engine.services.configuration.configuration_tasks.configuration_task_mock import (
    MockConfigurationTask,
)


class TestConfigureCommand(unittest.TestCase):
    """Configure command tests."""

    reader: MockConfigurationDataReaderService
    task_one: MockConfigurationTask
    task_two: MockConfigurationTask
    command: ConfigureCommand

    def setUp(self):
        self.reader = MockConfigurationDataReaderService()
        self.task_one = MockConfigurationTask()
        self.task_two = MockConfigurationTask()
        self.command = ConfigureCommand(self.reader, [self.task_one, self.task_two])

    def test_happy_path(self):
        """Happy path."""
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(self.task_one.configure_params, [self.reader.read_result])
        self.assertEqual(self.task_two.configure_params, [self.reader.read_result])

    def test_failed_task_stops_other_consecutive_tasks_from_being_executed(self):
        """Failed task stops other consecutive tasks from being executed."""
        # Arrange
        self.task_one.configure_result = OperationResult[bool].fail("Failure")

        # Act
        self.command.execute()

        # Assert
        self.assertEqual(self.task_one.configure_params, [self.reader.read_result])
        self.assertEqual(self.task_two.configure_params, [])

    def test_loads_stored_configuration_data(self):
        """Reads stored configuration data."""
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(self.reader.load_stored_triggered_times, 1)

    def test_reads_configuration_data_using_stored_data(self):
        """Reads configuration data using stored data."""
        # Arrange
        config_data = ConfigurationData.default()
        config_data.server_data_dir = "srv"
        self.reader.load_stored_result = config_data

        # Act
        self.command.execute()

        # Assert
        self.assertEqual(self.reader.read_params, [config_data])

    def test_configuration_data_read_is_passed_to_each_task(self):
        """Configuration data read is passed to each task."""
        # Arrange
        config_data = ConfigurationData.default()
        config_data.server_data_dir = "srv"
        self.reader.read_result = config_data

        # Act
        self.command.execute()

        # Assert
        self.assertEqual(self.task_one.configure_params, [config_data])
        self.assertEqual(self.task_two.configure_params, [config_data])
