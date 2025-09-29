import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import MockConfigurationContentReaderService
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import ReadParams
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService
from packages_engine.services.file_system.file_system_service_mock import WriteTextParams
from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.configuration.configuration_tasks.nftables import NftablesUbuntuConfigurationTask


class TestNftablesUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: NftablesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = NftablesUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
        self.data.server_data_dir = 'srv'
        self.reader.read_result = OperationResult[str].succeed(
            'nftables-config-result')

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_results_in_correct_notifications_flow(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'type': 'info', 'text': 'Reading Nftables Config template data.'},
                {'type': 'success',
                    'text': '\tReading Nftables Config template data successful.'},
                {'type': 'info', 'text': 'Writing Nftables Config data.'},
                {'type': 'success', 'text': '\tWriting Nftables Config data successful.'},
                {'type': 'info', 'text': 'Restarting Nftables'},
                {'type': 'success', 'text': '\tRestarting Nftables successful'},
            ]
        )

    def test_reads_config_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [ReadParams(ConfigurationContent.RAW_STRING, self.data,
                        '/usr/local/share/srv/data/nftables.conf')]
        )

    def test_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_read_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'type': 'info', 'text': 'Reading Nftables Config template data.'},
                {'type': 'error', 'text': '\tReading Nftables Config template data failed.'},
            ]
        )

    def test_writes_config_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams('/etc/nftables.conf',
                             'nftables-config-result')]
        )

    def test_write_failure_result_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_write_failure_result_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'type': 'info', 'text': 'Reading Nftables Config template data.'},
                {'type': 'success',
                    'text': '\tReading Nftables Config template data successful.'},
                {'type': 'info', 'text': 'Writing Nftables Config data.'},
                {'type': 'error', 'text': '\tWriting Nftables Config data failed.'},
            ]
        )

    def test_runs_correct_commands(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    'sudo nft -f /etc/nftables.conf',
                    'sudo systemctl restart nftables'
                    'sudo systemctl enable nftables'
                ]
            ]
        )

    def test_running_commands_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_running_commands_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'type': 'info', 'text': 'Reading Nftables Config template data.'},
                {'type': 'success',
                    'text': '\tReading Nftables Config template data successful.'},
                {'type': 'info', 'text': 'Writing Nftables Config data.'},
                {'type': 'success', 'text': '\tWriting Nftables Config data successful.'},
                {'type': 'info', 'text': 'Restarting Nftables'},
                {'type': 'error', 'text': '\tRestarting Nftables failed'},
            ]
        )
