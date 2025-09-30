import unittest

from packages_engine.models import OperationResult
from packages_engine.services.configuration.configuration_data_reader.configuration_data_reader_service_mock import MockConfigurationDataReaderService
from packages_engine.services.configuration.configuration_tasks.configuration_task_mock import MockConfigurationTask
from packages_engine.commands import ConfigureCommand


class TestAutostartCommand(unittest.TestCase):
    reader: MockConfigurationDataReaderService
    task_one: MockConfigurationTask
    task_two: MockConfigurationTask
    command: ConfigureCommand

    def setUp(self):
        self.reader = MockConfigurationDataReaderService()
        self.task_one = MockConfigurationTask()
        self.task_two = MockConfigurationTask()
        self.command = ConfigureCommand(
            self.reader, [self.task_one, self.task_two]
        )

    def test_happy_path(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.task_one.configure_params,
            [self.reader.read_result]
        )
        self.assertEqual(
            self.task_two.configure_params,
            [self.reader.read_result]
        )

    def test_failed_task_stops_other_consecutive_tasks_from_being_executed(self):
        # Arrange
        self.task_one.configure_result = OperationResult[bool].fail('Failure')

        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.task_one.configure_params,
            [self.reader.read_result]
        )
        self.assertEqual(
            self.task_two.configure_params,
            []
        )
