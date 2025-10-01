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
from packages_engine.services.configuration.configuration_tasks.docker import DockerUbuntuConfigurationTask


class TestDockerUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DockerUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DockerUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
        self.data.server_data_dir = 'srv'
        self.reader.read_result = OperationResult[str].succeed(
            'docker-compose-config-result')
        self.file_system.path_exists_result_map = {
            '/srv/gitea': False,
            '/srv/postgres': False,
            '/srv/pgadmin': False,
            '/srv/gitea/data': False,
            '/srv/gitea/config': False,
            '/srv/postgres/data': False,
            '/srv/pgadmin/data': False,
            '/srv/stack': False
        }
        self.controller.run_raw_commands_result_regex_map = {
            'sudo mkdir -p /srv/gitea': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/postgres': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/pgadmin': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/gitea/data': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/gitea/config': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/postgres/data': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/pgadmin/data': OperationResult[bool].succeed(True),
            'sudo mkdir -p /srv/stack': OperationResult[bool].succeed(True),
            'sudo chown -R 999:999 /srv/postgres/data': OperationResult[bool].succeed(True),
            'sudo chown -R 5050:5050 /srv/pgadmin/data': OperationResult[bool].succeed(True),
            'cd /srv/stack && sudo docker compose up -d': OperationResult[bool].succeed(True),
        }

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_creates_not_existing_paths(self):
        self._creates_not_existing_paths([])

    def test_gitea_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/gitea'])

    def test_postgres_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/postgres'])

    def test_pgadmin_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/pgadmin'])

    def test_gitea_data_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/gitea/data'])

    def test_gitea_config_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/gitea/config'])

    def test_postgres_data_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/postgres/data'])

    def test_pgadmin_data_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/pgadmin/data'])

    def test_srv_stack_folder_not_created_if_it_exists(self):
        self._creates_not_existing_paths(['/srv/stack'])

    def test_all_necessary_commands_are_run(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                ['sudo mkdir -p /srv/gitea'],
                ['sudo mkdir -p /srv/postgres'],
                ['sudo mkdir -p /srv/pgadmin'],
                ['sudo mkdir -p /srv/gitea/data'],
                ['sudo mkdir -p /srv/gitea/config'],
                ['sudo mkdir -p /srv/postgres/data'],
                ['sudo mkdir -p /srv/pgadmin/data'],
                ['sudo mkdir -p /srv/stack'],
                [
                    'sudo chown -R 999:999 /srv/postgres/data',
                    'sudo chown -R 5050:5050 /srv/pgadmin/data',
                    'sudo chmod -R 0755 /srv/postgres',
                    'sudo chmod -R 0755 /srv/gitea',
                    'sudo chmod -R 0755 /srv/pgadmin',
                    'sudo docker network create vpn-internal || true',
                    'sudo systemctl restart docker',
                    'cd /srv/stack && sudo docker compose down',
                    'sudo docker stop $(sudo docker ps -a -q) || true',
                    'sudo docker rm $(sudo docker ps -a -q) || true',
                    'sudo docker container prune -f',
                    'cd /srv/stack && sudo docker compose up -d'
                ]
            ]
        )

    def test_docker_config_template_file_is_read(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [ReadParams(ConfigurationContent.RAW_STRING, self.data,
                        '/usr/local/share/srv/data/docker-compose.yml')]
        )

    def test_docker_configuration_is_saved_correctly(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams('/srv/stack/docker-compose.yml',
                             'docker-compose-config-result')]
        )

    def test_notifications_happy_flow_is_correct(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration succeeded.', 'type': 'success'},
                {'text': 'Starting Docker containers.', 'type': 'info'},
                {'text': '\tStarting Docker containers succeeded.', 'type': 'success'}
            ]
        )

    def test_notifications_happy_flow_is_correct_when_all_directories_exist(self):
        # Arrange
        self.file_system.path_exists_result_map = {
            '/srv/gitea': True,
            '/srv/postgres': True,
            '/srv/pgadmin': True,
            '/srv/gitea/data': True,
            '/srv/gitea/config': True,
            '/srv/postgres/data': True,
            '/srv/pgadmin/data': True,
            '/srv/stack': True
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" exists. No need to create it again.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration succeeded.', 'type': 'success'},
                {'text': 'Starting Docker containers.', 'type': 'info'},
                {'text': '\tStarting Docker containers succeeded.', 'type': 'success'}
            ]
        )

    def test_task_results_in_failure_when_failing_to_create_gitea_folder(self):
        self._command_failure_results_in_failure('sudo mkdir -p /srv/gitea')

    def test_task_results_in_failure_when_failing_to_create_postgres_folder(self):
        self._command_failure_results_in_failure('sudo mkdir -p /srv/postgres')

    def test_task_results_in_failure_when_failing_to_create_pgadmin_folder(self):
        self._command_failure_results_in_failure('sudo mkdir -p /srv/pgadmin')

    def test_task_results_in_failure_when_failing_to_create_gitea_data_folder(self):
        self._command_failure_results_in_failure(
            'sudo mkdir -p /srv/gitea/data')

    def test_task_results_in_failure_when_failing_to_create_gitea_config_folder(self):
        self._command_failure_results_in_failure(
            'sudo mkdir -p /srv/gitea/config')

    def test_task_results_in_failure_when_failing_to_create_postgres_data_folder(self):
        self._command_failure_results_in_failure(
            'sudo mkdir -p /srv/postgres/data')

    def test_task_results_in_failure_when_failing_to_create_pgadmin_data_folder(self):
        self._command_failure_results_in_failure(
            'sudo mkdir -p /srv/pgadmin/data')

    def test_task_results_in_failure_when_failing_to_create_srv_stack_folder(self):
        self._command_failure_results_in_failure('sudo mkdir -p /srv/stack')

    def test_task_results_in_failure_when_failing_to_chown_postgres_data_folder(self):
        self._command_failure_results_in_failure(
            'sudo chown -R 999:999 /srv/postgres/data')

    def test_task_results_in_failure_when_failing_to_chown_pgadmin_data_folder(self):
        self._command_failure_results_in_failure(
            'sudo chown -R 5050:5050 /srv/pgadmin/data')

    def test_task_results_in_failure_when_failing_to_start_docker_containers(self):
        self._command_failure_results_in_failure(
            'cd /srv/stack && sudo docker compose up -d')

    def test_task_results_in_correct_notifications_when_failing_to_create_gitea_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/gitea',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_postgres_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/postgres',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_pgadmin_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/pgadmin',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_gitea_data_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/gitea/data',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.', 'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_gitea_config_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/gitea/config',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_postgres_data_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/postgres/data',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_pgadmin_data_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/pgadmin/data',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_create_srv_stack_folder(self):
        self._command_failure_results_in_notifications(
            'sudo mkdir -p /srv/stack',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" failed.',
                    'type': 'error'},
                {'text': '\tCreating directories operation failed.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_chown_postgres_data_folder(self):
        self._command_failure_results_in_notifications(
            'sudo chown -R 999:999 /srv/postgres/data',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration succeeded.', 'type': 'success'},
                {'text': 'Starting Docker containers.', 'type': 'info'},
                {'text': '\tFailed to start Docker containers.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_chown_pgadmin_data_folder(self):
        self._command_failure_results_in_notifications(
            'sudo chown -R 5050:5050 /srv/pgadmin/data',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration succeeded.', 'type': 'success'},
                {'text': 'Starting Docker containers.', 'type': 'info'},
                {'text': '\tFailed to start Docker containers.', 'type': 'error'}
            ]
        )

    def test_task_results_in_correct_notifications_when_failing_to_start_docker_containers(self):
        self._command_failure_results_in_notifications(
            'cd /srv/stack && sudo docker compose up -d',
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration succeeded.', 'type': 'success'},
                {'text': 'Starting Docker containers.', 'type': 'info'},
                {'text': '\tFailed to start Docker containers.', 'type': 'error'}
            ]
        )

    def test_read_failure_results_in_failed_task(self):
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_read_failure_results_in_correct_notifications_flow(self):
        fail_result = OperationResult[str].fail('Failure')
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data failed.', 'type': 'error'}
            ]
        )

    def test_write_failure_results_in_failed_task(self):
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_write_failure_results_in_correct_notifications_flow(self):
        fail_result = OperationResult[bool].fail('Failure')
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Creating directories if needed.', 'type': 'info'},
                {'text': '\tCreating directory "/srv/gitea" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/gitea/config" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/gitea/config" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/gitea/config" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/postgres/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/postgres/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/postgres/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/pgadmin/data" if needed.',
                    'type': 'info'},
                {'text': '\t\tDirectory "/srv/pgadmin/data" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/pgadmin/data" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directory "/srv/stack" if needed.', 'type': 'info'},
                {'text': '\t\tDirectory "/srv/stack" does not exist. Creating it now.',
                    'type': 'info'},
                {'text': '\t\tCreation of the directory "/srv/stack" succeeded.',
                    'type': 'success'},
                {'text': '\tCreating directories operation succeeded.', 'type': 'success'},
                {'text': 'Reading Docker Config template data.', 'type': 'info'},
                {'text': '\tReading Docker Config template data succeeded.',
                    'type': 'success'},
                {'text': 'Writing Docker configuration.', 'type': 'info'},
                {'text': '\tWriting Docker configuration failed.', 'type': 'error'}
            ]
        )

    def _creates_not_existing_paths(self, existing_paths: list[str]):
        # Arrange
        for existing_path in existing_paths:
            self.file_system.path_exists_result_map[existing_path] = True

        # Act
        self.task.configure(self.data)

        # Assert
        expected_commands = [
            'sudo mkdir -p /srv/gitea',
            'sudo mkdir -p /srv/postgres',
            'sudo mkdir -p /srv/pgadmin',
            'sudo mkdir -p /srv/gitea/data',
            'sudo mkdir -p /srv/gitea/config',
            'sudo mkdir -p /srv/postgres/data',
            'sudo mkdir -p /srv/pgadmin/data',
            'sudo mkdir -p /srv/stack',
        ]
        actual_commands: list[str] = []
        params_list = self.controller.run_raw_commands_params
        for params in params_list:
            for param in params:
                actual_commands.append(param)

        for expected_command in expected_commands:
            ignore = False
            for path in existing_paths:
                command = f'sudo mkdir -p {path}'
                if command == expected_command:
                    ignore = True
                    break
            if ignore:
                continue
            if not expected_command in actual_commands:
                self.fail(
                    f'Expecting "{expected_command}" which was not found among actual commands.')

    def _command_failure_results_in_failure(self, command: str):
        # Arrange
        self.controller.run_raw_commands_result_regex_map.pop(
            'sudo chown -R 999:999 /srv/postgres/data')
        self.controller.run_raw_commands_result_regex_map.pop(
            'sudo chown -R 5050:5050 /srv/pgadmin/data')
        self.controller.run_raw_commands_result_regex_map.pop(
            'cd /srv/stack && sudo docker compose up -d')
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def _command_failure_results_in_notifications(self, command: str, expected_notifications: list[object]):
        # Arrange
        self.controller.run_raw_commands_result_regex_map.pop(
            'sudo chown -R 999:999 /srv/postgres/data')
        self.controller.run_raw_commands_result_regex_map.pop(
            'sudo chown -R 5050:5050 /srv/pgadmin/data')
        self.controller.run_raw_commands_result_regex_map.pop(
            'cd /srv/stack && sudo docker compose up -d')
        fail_result = OperationResult[bool].fail('Failure')
        self.controller.run_raw_commands_result_regex_map[command] = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            expected_notifications
        )
