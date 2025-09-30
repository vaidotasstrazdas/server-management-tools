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
from packages_engine.services.configuration.configuration_tasks.nginx import NginxUbuntuConfigurationTask


class TestNginxUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: NginxUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = NginxUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
        self.data.domain_name = 'internal.app'
        self.data.clients_data_dir = '/dev/usb/client'
        self.data.server_data_dir = 'srv'
        self.file_system.path_exists_result_map = {
            '/etc/ssl/internal-pki': False,
            '/etc/ssl/internal-pki/san.cnf': False,
            '/etc/ssl/internal-pki/internal.app.key': False,
            '/etc/ssl/internal-pki/internal.app.csr': False,
            '/etc/ssl/internal-pki/internal.app.crt': False,
            '/etc/ssl/certs/internal.crt': False,
            '/etc/ssl/private/internal.key': False,
        }

        self.file_system.remove_location_result_map = {
            '/etc/ssl/internal-pki': OperationResult[bool].succeed(True),
            '/etc/ssl/internal-pki/san.cnf': OperationResult[bool].succeed(True),
            '/etc/ssl/internal-pki/internal.app.key': OperationResult[bool].succeed(True),
            '/etc/ssl/internal-pki/internal.app.csr': OperationResult[bool].succeed(True),
            '/etc/ssl/internal-pki/internal.app.crt': OperationResult[bool].succeed(True),
            '/etc/ssl/certs/internal.crt': OperationResult[bool].succeed(True),
            '/etc/ssl/private/internal.key': OperationResult[bool].succeed(True),
        }

        self.file_system.write_text_result_map = {
            '/etc/ssl/internal-pki/san.cnf': OperationResult[bool].succeed(True),
            '/dev/usb/client/internal.app.crt': OperationResult[bool].succeed(True)
        }
        self.file_system.read_text_result = OperationResult[str].succeed(
            'ca-result')

        self.reader.read_result = OperationResult[str].succeed(
            'ssl-config-read-result')

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_removes_existing_pki_files_case_1(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki'
        ])

    def test_removes_existing_pki_files_case_2(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki',
            '/etc/ssl/internal-pki/san.cnf'
        ])

    def test_removes_existing_pki_files_case_3(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki',
            '/etc/ssl/internal-pki/san.cnf',
            '/etc/ssl/internal-pki/internal.app.key'
        ])

    def test_removes_existing_pki_files_case_4(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki',
            '/etc/ssl/internal-pki/san.cnf',
            '/etc/ssl/internal-pki/internal.app.key',
            '/etc/ssl/internal-pki/internal.app.csr'
        ])

    def test_removes_existing_pki_files_case_5(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki',
            '/etc/ssl/internal-pki/san.cnf',
            '/etc/ssl/internal-pki/internal.app.key',
            '/etc/ssl/internal-pki/internal.app.csr',
            '/etc/ssl/internal-pki/internal.app.crt'
        ])

    def test_removes_existing_pki_files_case_6(self):
        self._existing_pki_files_removal_test([
            '/etc/ssl/internal-pki',
            '/etc/ssl/internal-pki/san.cnf',
            '/etc/ssl/internal-pki/internal.app.key',
            '/etc/ssl/internal-pki/internal.app.csr',
            '/etc/ssl/internal-pki/internal.app.crt',
            '/etc/ssl/certs/internal.crt'
        ])

    def test_does_not_remove_any_pki_files_when_all_pki_files_exist(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/etc/ssl/internal-pki': True,
            '/etc/ssl/internal-pki/san.cnf': True,
            '/etc/ssl/internal-pki/internal.app.key': True,
            '/etc/ssl/internal-pki/internal.app.csr': True,
            '/etc/ssl/internal-pki/internal.app.crt': True,
            '/etc/ssl/certs/internal.crt': True,
            '/etc/ssl/private/internal.key': True,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.remove_location_params,
            []
        )

    def test_location_removal_failure_case_1(self):
        self._failed_remove_location_test(
            '/etc/ssl/internal-pki'
        )

    def test_location_removal_failure_case_2(self):
        self._failed_remove_location_test(
            '/etc/ssl/internal-pki/san.cnf'
        )

    def test_location_removal_failure_case_3(self):
        self._failed_remove_location_test(
            '/etc/ssl/internal-pki/internal.app.key'
        )

    def test_location_removal_failure_case_4(self):
        self._failed_remove_location_test(
            '/etc/ssl/internal-pki/internal.app.csr'
        )

    def test_location_removal_failure_case_5(self):
        self._failed_remove_location_test(
            '/etc/ssl/internal-pki/internal.app.crt'
        )

    def test_location_removal_failure_case_6(self):
        self._failed_remove_location_test(
            '/etc/ssl/certs/internal.crt'
        )

    def test_location_removal_failure_case_7(self):
        self._failed_remove_location_test(
            '/etc/ssl/private/internal.key'
        )

    def test_location_removal_failure_notifications_case_1(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/internal-pki'
        )

    def test_location_removal_failure_notifications_case_2(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/internal-pki/san.cnf'
        )

    def test_location_removal_failure_notifications_case_3(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/internal-pki/internal.app.key'
        )

    def test_location_removal_failure_notifications_case_4(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/internal-pki/internal.app.csr'
        )

    def test_location_removal_failure_notifications_case_5(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/internal-pki/internal.app.crt'
        )

    def test_location_removal_failure_notifications_case_6(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/certs/internal.crt'
        )

    def test_location_removal_failure_notifications_case_7(self):
        self._failed_remove_location_notifications_test(
            '/etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_task_failure_case_1(self):
        self._failed_command_test(
            'sudo mkdir -p /etc/ssl/internal-pki'
        )

    def test_failed_command_results_in_task_failure_case_2(self):
        self._failed_command_test(
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096'
        )

    def test_failed_command_results_in_task_failure_case_3(self):
        self._failed_command_test(
            'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt'
        )

    def test_failed_command_results_in_task_failure_case_4(self):
        self._failed_command_test(
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out internal.app.key 2048'
        )

    def test_failed_command_results_in_task_failure_case_5(self):
        self._failed_command_test(
            'cd /etc/ssl/internal-pki && sudo openssl req -new -key internal.app.key -out internal.app.csr -config san.cnf'
        )

    def test_failed_command_results_in_task_failure_case_6(self):
        self._failed_command_test(
            'cd /etc/ssl/internal-pki && sudo openssl x509 -req -in internal.app.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out internal.app.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf'
        )

    def test_failed_command_results_in_task_failure_case_7(self):
        self._failed_command_test(
            'sudo cp /etc/ssl/internal-pki/internal.app.crt /etc/ssl/certs/internal.crt'
        )

    def test_failed_command_results_in_task_failure_case_8(self):
        self._failed_command_test(
            'sudo cp /etc/ssl/internal-pki/internal.app.key /etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_task_failure_case_9(self):
        self._failed_command_test(
            'sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_task_failure_case_10(self):
        self._failed_command_test(
            'sudo chmod 644 /etc/ssl/certs/internal.crt'
        )

    def test_failed_command_results_in_task_failure_case_11(self):
        self._failed_command_test(
            'sudo chmod 600 /etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_correct_notifications_case_1(self):
        self._failed_command_notifications_test(
            'sudo mkdir -p /etc/ssl/internal-pki',
            [
                {'text': 'Creating PKI if needed.', 'type': 'info'},
                {'text': 'Checking if PKI is configured', 'type': 'info'},
                {'text': '\tPKI is not configured. Will remove unnecessary files',
                    'type': 'info'},
                {'text': '\tFailed to create PKI folder.', 'type': 'error'}
            ]
        )

    def test_failed_command_results_in_correct_notifications_case_2(self):
        self._failed_command_notifications_test(
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096'
        )

    def test_failed_command_results_in_correct_notifications_case_3(self):
        self._failed_command_notifications_test(
            'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt'
        )

    def test_failed_command_results_in_correct_notifications_case_4(self):
        self._failed_command_notifications_test(
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out internal.app.key 2048'
        )

    def test_failed_command_results_in_correct_notifications_case_5(self):
        self._failed_command_notifications_test(
            'cd /etc/ssl/internal-pki && sudo openssl req -new -key internal.app.key -out internal.app.csr -config san.cnf'
        )

    def test_failed_command_results_in_correct_notifications_case_6(self):
        self._failed_command_notifications_test(
            'cd /etc/ssl/internal-pki && sudo openssl x509 -req -in internal.app.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out internal.app.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf'
        )

    def test_failed_command_results_in_correct_notifications_case_7(self):
        self._failed_command_notifications_test(
            'sudo cp /etc/ssl/internal-pki/internal.app.crt /etc/ssl/certs/internal.crt'
        )

    def test_failed_command_results_in_correct_notifications_case_8(self):
        self._failed_command_notifications_test(
            'sudo cp /etc/ssl/internal-pki/internal.app.key /etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_correct_notifications_case_9(self):
        self._failed_command_notifications_test(
            'sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key'
        )

    def test_failed_command_results_in_correct_notifications_case_10(self):
        self._failed_command_notifications_test(
            'sudo chmod 644 /etc/ssl/certs/internal.crt'
        )

    def test_failed_command_results_in_correct_notifications_case_11(self):
        self._failed_command_notifications_test(
            'sudo chmod 600 /etc/ssl/private/internal.key'
        )

    def test_reads_ssl_template_config_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    '/usr/local/share/srv/data/ssl.conf'
                )
            ]
        )

    def test_ssl_config_template_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_ssl_config_template_read_failure_results_in_correct_notifications_flow(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating PKI if needed.', 'type': 'info'},
                {'text': 'Checking if PKI is configured', 'type': 'info'},
                {'text': '\tPKI is not configured. Will remove unnecessary files',
                    'type': 'info'},
                {'text': '\tPKI folder created successfully.', 'type': 'success'},
                {'text': 'Reading SSL configuration template.', 'type': 'info'},
                {'text': '\tFailed to read SSL configuration.', 'type': 'error'}
            ]
        )

    def test_correct_file_system_writes_are_performed(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams(
                    '/etc/ssl/internal-pki/san.cnf',
                    'ssl-config-read-result'
                ),
                WriteTextParams(
                    '/dev/usb/client/internal.app.crt',
                    'ca-result'
                )
            ]
        )

    def test_san_cnf_write_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result_map['/etc/ssl/internal-pki/san.cnf'] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_client_ca_config_write_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result_map['/dev/usb/client/internal.app.crt'] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_san_cnf_write_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result_map['/etc/ssl/internal-pki/san.cnf'] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating PKI if needed.', 'type': 'info'},
                {'text': 'Checking if PKI is configured', 'type': 'info'},
                {'text': '\tPKI is not configured. Will remove unnecessary files',
                    'type': 'info'},
                {'text': '\tPKI folder created successfully.', 'type': 'success'},
                {'text': 'Reading SSL configuration template.', 'type': 'info'},
                {'text': '\tSSL Configuration template read successfull.',
                    'type': 'success'},
                {'text': 'Saving SSL configuration.', 'type': 'info'},
                {'text': '\tSaving SSL configuration failed.', 'type': 'error'}
            ]
        )

    def test_client_ca_config_write_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result_map['/dev/usb/client/internal.app.crt'] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating PKI if needed.', 'type': 'info'},
                {'text': 'Checking if PKI is configured', 'type': 'info'},
                {'text': '\tPKI is not configured. Will remove unnecessary files',
                    'type': 'info'},
                {'text': '\tPKI folder created successfully.', 'type': 'success'},
                {'text': 'Reading SSL configuration template.', 'type': 'info'},
                {'text': '\tSSL Configuration template read successfull.',
                    'type': 'success'},
                {'text': 'Saving SSL configuration.', 'type': 'info'},
                {'text': '\tSSL Configuration saved successfully.', 'type': 'success'},
                {'text': 'Running commands to create private and public keys if needed.', 'type': 'info'},
                {'text': '\tCommands succeeded.', 'type': 'success'},
                {'text': 'Reading certificate authority configuration file.',
                    'type': 'info'},
                {'text': '\tReading certificate authority configuration file succeeded.', 'type': 'error'},
                {'text': 'Saving certificate authority configuration file on the external device.', 'type': 'info'},
                {'text': '\tSaving certificate authority configuration file on the external device failed.', 'type': 'error'}
            ]
        )

    def test_reads_ca_data_using_correct_parameters(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(self.file_system.read_text_params,
                         ['/etc/ssl/internal-pki/ca.crt'])

    def test_ca_read_failure_results_in_task_failure(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.file_system.read_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_ca_read_failure_results_in_correct_notifications(self):
        # Arrange
        fail_result = OperationResult[str].fail('Failure')
        self.file_system.read_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating PKI if needed.', 'type': 'info'},
                {'text': 'Checking if PKI is configured', 'type': 'info'},
                {'text': '\tPKI is not configured. Will remove unnecessary files',
                    'type': 'info'},
                {'text': '\tPKI folder created successfully.', 'type': 'success'},
                {'text': 'Reading SSL configuration template.', 'type': 'info'},
                {'text': '\tSSL Configuration template read successfull.',
                    'type': 'success'},
                {'text': 'Saving SSL configuration.', 'type': 'info'},
                {'text': '\tSSL Configuration saved successfully.', 'type': 'success'},
                {'text': 'Running commands to create private and public keys if needed.',
                    'type': 'info'},
                {'text': '\tCommands succeeded.', 'type': 'success'},
                {'text': 'Reading certificate authority configuration file.',
                    'type': 'info'},
                {'text': '\tReading certificate authority configuration file failed.',
                    'type': 'error'}
            ]
        )

    def _existing_pki_files_removal_test(self, existing_files: list[str]):
        # Arrange
        for file in existing_files:
            self.file_system.path_exists_result_map[file] = True

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.remove_location_params,
            existing_files
        )

    def _failed_remove_location_test(self, location: str):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.path_exists_result_map[location] = True
        self.file_system.remove_location_result_map[location] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _failed_command_test(self, command: str):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _failed_remove_location_notifications_test(self, location: str):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.path_exists_result_map[location] = True
        self.file_system.remove_location_result_map[location] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        expected_notifications = [
            {'text': 'Creating PKI if needed.', 'type': 'info'},
            {'text': 'Checking if PKI is configured', 'type': 'info'},
            {'text': '\tPKI is not configured. Will remove unnecessary files',
                'type': 'info'},
            {'text': f'\tRemoving "{location}"', 'type': 'info'},
            {'text': f'\t\tRemoving "{location}" failed', 'type': 'error'}

        ]
        self.assertEqual(self.notifications.params, expected_notifications)

    def _failed_command_notifications_test(self, command: str, expected_notifications: list[object] | None = None):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        final_expected_notifications = [
            {'text': 'Creating PKI if needed.', 'type': 'info'},
            {'text': 'Checking if PKI is configured', 'type': 'info'},
            {'text': '\tPKI is not configured. Will remove unnecessary files',
                'type': 'info'},
            {'text': '\tPKI folder created successfully.', 'type': 'success'},
            {'text': 'Reading SSL configuration template.', 'type': 'info'},
            {'text': '\tSSL Configuration template read successfull.', 'type': 'success'},
            {'text': 'Saving SSL configuration.', 'type': 'info'},
            {'text': '\tSSL Configuration saved successfully.', 'type': 'success'},
            {'text': 'Running commands to create private and public keys if needed.', 'type': 'info'},
            {'text': '\tCommands failed.', 'type': 'error'}
        ]
        if expected_notifications != None:
            final_expected_notifications = expected_notifications
        self.assertEqual(self.notifications.params,
                         final_expected_notifications)
