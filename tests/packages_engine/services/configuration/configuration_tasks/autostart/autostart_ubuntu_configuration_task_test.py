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
from packages_engine.services.configuration.configuration_tasks.autostart import AutostartUbuntuConfigurationTask


class TestAutostartUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: AutostartUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = AutostartUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
        self.data.server_data_dir = 'srv'
        self.reader.read_result = OperationResult[str].succeed(
            'autostart content'
        )

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_results_in_correct_notifications(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Configuring autostart script', 'type': 'info'},
                {'text': '\tAutostart service template read successfully',
                    'type': 'success'},
                {'text': 'Saving autostart configuration in the system.', 'type': 'info'},
                {'text': '\tAutostart service configuration saved in the system successfully',
                    'type': 'success'},
                {'text': 'Enabling autostart service', 'type': 'info'},
                {'text': '\tAutostart service enabled successfully', 'type': 'success'}
            ]
        )

    def test_reads_autostart_config_template_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    '/usr/local/share/srv/data/autostart.service'
                )
            ]
        )

    def test_autostart_config_template_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_autostart_config_template_read_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Configuring autostart script', 'type': 'info'},
                {'text': '\tFailed to read autostart service template', 'type': 'error'}
            ]
        )

    def test_autostart_config_is_saved_in_the_system(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams(
                    '/etc/systemd/system/autostart.service',
                    'autostart content'
                )
            ]
        )

    def test_autostart_config_save_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_autostart_config_save_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Configuring autostart script', 'type': 'info'},
                {'text': '\tAutostart service template read successfully',
                    'type': 'success'},
                {'text': 'Saving autostart configuration in the system.', 'type': 'info'},
                {'text': '\tFailed to save/overwrite autostart service', 'type': 'error'}
            ]
        )

    def test_commands_to_enable_autostart_service_are_run(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    'sudo systemctl daemon-reload',
                    'sudo systemctl enable autostart.service',
                    'sudo systemctl start autostart.service'
                ]
            ]
        )

    def test_commands_to_enable_autostart_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_commands_to_enable_autostart_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Configuring autostart script', 'type': 'info'},
                {'text': '\tAutostart service template read successfully',
                    'type': 'success'},
                {'text': 'Saving autostart configuration in the system.', 'type': 'info'},
                {'text': '\tAutostart service configuration saved in the system successfully',
                    'type': 'success'},
                {'text': 'Enabling autostart service', 'type': 'info'},
                {'text': '\tFailed to enable autostart service', 'type': 'error'}
            ]
        )
