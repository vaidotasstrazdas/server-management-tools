from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class NftablesUbuntuConfigurationTask(ConfigurationTask):
    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:

        self.notifications.info('Reading Nftables Config template data.')
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f'/usr/local/share/{data.server_data_dir}/data/nftables.conf'
        )

        if not read_result.success or read_result.data == None:
            self.notifications.error(
                '\tReading Nftables Config template data failed.')
            return read_result.as_fail()
        self.notifications.success(
            '\tReading Nftables Config template data successful.')

        self.notifications.info('Writing Nftables Config data.')
        write_text_result = self.file_system.write_text(
            '/etc/nftables.conf', read_result.data)
        if not write_text_result.success:
            self.notifications.error('\tWriting Nftables Config data failed.')
            return write_text_result.as_fail()
        self.notifications.success(
            '\tWriting Nftables Config data successful.')

        self.notifications.info('Restarting Nftables')
        run_commands_result = self.controller.run_raw_commands([
            'sudo nft -f /etc/nftables.conf',
            'sudo systemctl restart nftables'
            'sudo systemctl enable nftables'
        ])
        if not run_commands_result.success:
            self.notifications.error('\tRestarting Nftables failed')
            return run_commands_result.as_fail()
        self.notifications.success('\tRestarting Nftables successful')

        return OperationResult[bool].succeed(True)
