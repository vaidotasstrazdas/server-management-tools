from typing import Optional

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
from packages_engine.services.configuration.configuration_tasks.wireguard import WireguardUbuntuConfigurationTask

_server_config_read_result_successful = True
_shared_config_read_result_successful = True


def _read_config(content: ConfigurationContent, config: ConfigurationData, template_path: Optional[str] = None) -> OperationResult[str]:
    if content == ConfigurationContent.WIREGUARD_SERVER_CONFIG:
        if not _server_config_read_result_successful:
            return OperationResult[str].fail('wireguard-server-config-read-failure')
        return OperationResult[str].succeed('wireguard-server-config')

    if content == ConfigurationContent.WIREGUARD_CLIENTS_CONFIG:
        if not _shared_config_read_result_successful:
            return OperationResult[str].fail('wireguard-clients-config-read-failure')
        return OperationResult[str].succeed('wireguard-clients-config')

    return OperationResult[str].succeed('')


class TestWireguardUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: WireguardUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = WireguardUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
        self.data.wireguard_client_names = ['client_one', 'client_two']
        self.data.clients_data_dir = '/dev/usb/wireguard_clients'

        self.file_system.path_exists_result_map = {
            '/etc/wireguard/clients/client_one.key': False,
            '/etc/wireguard/clients/client_one.pub': False,
            '/etc/wireguard/clients/client_two.key': False,
            '/etc/wireguard/clients/client_two.pub': False
        }

        self.file_system.write_text_result_map = {
            '/etc/wireguard/wg0.conf': OperationResult[bool].succeed(True),
            '/dev/usb/wireguard_clients/wireguard_clients.config': OperationResult[bool].succeed(True)
        }

        self.reader.read_result_fn = _read_config
        global _server_config_read_result_successful
        global _shared_config_read_result_successful
        _server_config_read_result_successful = True
        _shared_config_read_result_successful = True

    def tearDown(self):
        global _server_config_read_result_successful
        global _shared_config_read_result_successful
        _server_config_read_result_successful = True
        _shared_config_read_result_successful = True

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_checks_if_client_related_files_exist(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/etc/wireguard/clients/client_one.key': True,
            '/etc/wireguard/clients/client_one.pub': True,
            '/etc/wireguard/clients/client_two.key': True,
            '/etc/wireguard/clients/client_two.pub': True
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.path_exists_params,
            [
                '/etc/wireguard/clients/client_one.key',
                '/etc/wireguard/clients/client_one.pub',
                '/etc/wireguard/clients/client_two.key',
                '/etc/wireguard/clients/client_two.pub'
            ]
        )

    def test_executes_configuration_commands_when_clients_do_not_exist_case_1(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    'umask 077',
                    f'wg genkey | tee /etc/wireguard/clients/client_one.key | wg pubkey > /etc/wireguard/clients/client_one.pub'
                ],
                [
                    'umask 077',
                    f'wg genkey | tee /etc/wireguard/clients/client_two.key | wg pubkey > /etc/wireguard/clients/client_two.pub'
                ]
            ]
        )

    def test_executes_configuration_commands_when_clients_do_not_exist_case_2(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/etc/wireguard/clients/client_one.key': True,
            '/etc/wireguard/clients/client_one.pub': True,
            '/etc/wireguard/clients/client_two.key': False,
            '/etc/wireguard/clients/client_two.pub': True
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    'umask 077',
                    f'wg genkey | tee /etc/wireguard/clients/client_two.key | wg pubkey > /etc/wireguard/clients/client_two.pub'
                ]
            ]
        )

    def test_informs_when_client_exists(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/etc/wireguard/clients/client_one.key': True,
            '/etc/wireguard/clients/client_one.pub': True,
            '/etc/wireguard/clients/client_two.key': True,
            '/etc/wireguard/clients/client_two.pub': True
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'type': 'info', 'text': 'Client "client_one" has WireGuard configuration already. Nothing needs to be done.'},
                {'type': 'info', 'text': 'Client "client_two" has WireGuard configuration already. Nothing needs to be done.'}
            ]
        )

    def test_existing_clients_return_success_if_other_operations_succeed(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/etc/wireguard/clients/client_one.key': True,
            '/etc/wireguard/clients/client_one.pub': True,
            '/etc/wireguard/clients/client_two.key': True,
            '/etc/wireguard/clients/client_two.pub': True
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_failure_to_configure_client_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_reads_correct_wireguard_configurations(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.WIREGUARD_SERVER_CONFIG, self.data),
                ReadParams(
                    ConfigurationContent.WIREGUARD_CLIENTS_CONFIG, self.data)
            ]
        )

    def test_failure_to_read_wireguard_server_configuration_results_in_failure(self):
        # Arrange
        global _server_config_read_result_successful
        _server_config_read_result_successful = False

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[str].fail(
            'wireguard-server-config-read-failure'))

    def test_failure_to_read_wireguard_client_configuration_results_in_failure(self):
        # Arrange
        global _shared_config_read_result_successful
        _shared_config_read_result_successful = False

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[str].fail(
            'wireguard-clients-config-read-failure'))

    def test_failure_to_save_wireguard_server_config_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Massive fail')
        self.file_system.write_text_result_map = {
            '/etc/wireguard/wg0.conf': fail_result,
            '/dev/usb/wireguard_clients/wireguard_clients.config': OperationResult[bool].succeed(True)
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_failure_to_save_wireguard_shared_config_results_in_failure(self):
        # Arrange
        fail_result = OperationResult[bool].fail('Massive fail')
        self.file_system.write_text_result_map = {
            '/etc/wireguard/wg0.conf': OperationResult[bool].succeed(True),
            '/dev/usb/wireguard_clients/wireguard_clients.config': fail_result
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_inserts_correct_config_texts_into_correct_files(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams('/etc/wireguard/wg0.conf',
                                'wireguard-server-config'),
                WriteTextParams(
                    '/dev/usb/wireguard_clients/wireguard_clients.config', 'wireguard-clients-config')
            ]
        )
