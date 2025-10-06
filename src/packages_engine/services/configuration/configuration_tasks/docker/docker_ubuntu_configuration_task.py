from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract

# add your primary user; for Multipass it's 'ubuntu'
# sudo usermod -aG docker ubuntu
# inform that a new login is required for the group to take effect:
# echo "Re-login or run: newgrp docker"


class DockerUbuntuConfigurationTask(ConfigurationTask):
    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        create_result = self._create_directories_if_needed([
            '/srv/gitea',
            '/srv/postgres',
            '/srv/pgadmin',
            '/srv/gitea/data',
            '/srv/gitea/config',
            '/srv/postgres/data',
            '/srv/pgadmin/data',
            '/srv/stack',
        ])

        if not create_result.success:
            return create_result.as_fail()

        self.notifications.info('Reading Docker Config template data.')
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f'/usr/local/share/{data.server_data_dir}/data/docker-compose.yml'
        )

        if not read_result.success or read_result.data == None:
            self.notifications.error(
                '\tReading Docker Config template data failed.')
            return read_result.as_fail()
        self.notifications.success(
            '\tReading Docker Config template data succeeded.')

        self.notifications.info('Writing Docker configuration.')
        write_result = self.file_system.write_text(
            '/srv/stack/docker-compose.yml', read_result.data)
        if not write_result.success:
            self.notifications.error('\tWriting Docker configuration failed.')
            return write_result.as_fail()
        self.notifications.success('\tWriting Docker configuration succeeded.')

        self.notifications.info('Starting Docker containers.')
        start_result = self.controller.run_raw_commands([
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
        ])
        if not start_result.success:
            self.notifications.error('\tFailed to start Docker containers.')
            return start_result.as_fail()
        self.notifications.success('\tStarting Docker containers succeeded.')

        return OperationResult[bool].succeed(True)

    def _create_directories_if_needed(self, directories: list[str]) -> OperationResult[bool]:
        self.notifications.info('Creating directories if needed.')
        for directory in directories:
            create_result = self._create_directory_if_needed(directory)
            if not create_result.success:
                self.notifications.error(
                    '\tCreating directories operation failed.')
                return create_result.as_fail()
        self.notifications.success(
            '\tCreating directories operation succeeded.')

        return OperationResult[bool].succeed(True)

    def _create_directory_if_needed(self, directory: str) -> OperationResult[bool]:
        self.notifications.info(
            f'\tCreating directory "{directory}" if needed.')
        if self.file_system.path_exists(directory):
            self.notifications.success(
                f'\t\tDirectory "{directory}" exists. No need to create it again.')
            return OperationResult[bool].succeed(True)

        self.notifications.info(
            f'\t\tDirectory "{directory}" does not exist. Creating it now.')
        create_result = self.controller.run_raw_commands(
            [f'sudo mkdir -p {directory}'])
        if not create_result.success:
            self.notifications.error(
                f'\t\tCreation of the directory "{directory}" failed.')
            return create_result.as_fail()
        self.notifications.success(
            f'\t\tCreation of the directory "{directory}" succeeded.')

        return OperationResult[bool].succeed(True)
