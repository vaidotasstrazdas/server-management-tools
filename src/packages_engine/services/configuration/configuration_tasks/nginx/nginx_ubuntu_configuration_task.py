from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class NginxUbuntuConfigurationTask(ConfigurationTask):
    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info('Creating PKI folder if needed.')
        if self.file_system.path_exists('/etc/ssl/internal-pki'):
            self.notifications.success(
                '\tPKI configured already. Nothing needs to be done.')
            return OperationResult[bool].succeed(True)

        create_result = self.controller.run_raw_commands(
            ['sudo mkdir -p /etc/ssl/internal-pki'])
        if not create_result.success:
            self.notifications.error('\tFailed to create PKI folder.')
            return create_result.as_fail()
        self.notifications.success('\tPKI folder created successfully.')

        self.notifications.info('Reading SSL configuration template.')
        ssl_read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f'/usr/local/share/{data.server_data_dir}/data/ssl.conf'
        )
        if not ssl_read_result.success or ssl_read_result.data == None:
            self.notifications.error('\tFailed to read SSL configuration.')
            return ssl_read_result.as_fail()
        self.notifications.success(
            '\tSSL Configuration template read successfull.')

        self.notifications.info('Saving SSL configuration.')
        write_result = self.file_system.write_text(
            '/etc/ssl/internal-pki/san.cnf', ssl_read_result.data)
        if not write_result.success:
            self.notifications.error('\tSaving SSL configuration failed.')
            return write_result.as_fail()
        self.notifications.success(
            '\tSSL Configuration saved successfully.')

        self.notifications.info(
            'Running commands to create private and public keys if needed.')
        run_result = self.controller.run_raw_commands([
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096',
            'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt',
            f'cd /etc/ssl/internal-pki && sudo openssl genrsa -out {data.domain_name}.key 2048',
            f'cd /etc/ssl/internal-pki && sudo openssl req -new -key {data.domain_name}.key -out {data.domain_name}.csr -config san.cnf',
            f'cd /etc/ssl/internal-pki && sudo openssl x509 -req -in {data.domain_name}.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out {data.domain_name}.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf',
            f'sudo cp /etc/ssl/internal-pki/{data.domain_name}.crt /etc/ssl/certs/internal.crt',
            f'sudo cp /etc/ssl/internal-pki/{data.domain_name}.key /etc/ssl/private/internal.key',
            'sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key',
            'sudo chmod 644 /etc/ssl/certs/internal.crt',
            'sudo chmod 600 /etc/ssl/private/internal.key',
        ])
        if not run_result.success:
            self.notifications.error('\tCommands failed.')
            return run_result.as_fail()
        self.notifications.success('\tCommands succeeded.')

        self.notifications.info(
            'Reading certificate authority configuration file.')
        ca_read_result = self.file_system.read_text(
            '/etc/ssl/internal-pki/ca.crt')
        if not ca_read_result.success or ca_read_result.data == None:
            self.notifications.error(
                '\tReading certificate authority configuration file failed.')
            return ca_read_result.as_fail()
        self.notifications.error(
            '\tReading certificate authority configuration file succeeded.')

        self.notifications.info(
            'Saving certificate authority configuration file on the external device.')
        write_crt_result = self.file_system.write_text(
            f'{data.clients_data_dir}/{data.domain_name}.crt', ca_read_result.data)
        if not write_crt_result.success:
            self.notifications.error(
                '\tSaving certificate authority configuration file on the external device failed.')
            return write_crt_result.as_fail()
        self.notifications.success(
            '\tSaving certificate authority configuration file on the external device succeeded.')

        return OperationResult[bool].succeed(True)
