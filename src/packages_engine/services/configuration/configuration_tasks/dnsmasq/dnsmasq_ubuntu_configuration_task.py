from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract

# NOTE:
# Dnsmasq and systemd-resolved both manage DNS on port 53.
# Configuration task must disable systemd-resolved (DNSStubListener=no)
# or bind dnsmasq to a non-conflicting interface/address.


class DnsmasqUbuntuConfigurationTask(ConfigurationTask):
    """ Dnsmasq configuration task. """

    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info('Reading Dnsmasq Config template data.')
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f'/usr/local/share/{data.server_data_dir}/data/dnsmasq.conf'
        )

        if not read_result.success or read_result.data is None:
            self.notifications.error(
                '\tReading Dnsmasq Config template data failed.'
            )
            return read_result.as_fail()
        self.notifications.success(
            '\tReading Dnsmasq Config template data successful.'
        )

        self.notifications.info('Writing Dnsmasq Config data.')
        write_text_result = self.file_system.write_text(
            '/etc/dnsmasq.d/internal.conf',
            read_result.data
        )
        if not write_text_result.success:
            self.notifications.error('\tWriting Dnsmasq Config data failed.')
            return write_text_result.as_fail()
        self.notifications.success('\tWriting Dnsmasq Config data successful.')

        self.notifications.info('Restarting Dnsmasq')
        run_commands_result = self.controller.run_raw_commands([
            'sudo systemctl restart dnsmasq',
            'sudo systemctl enable dnsmasq'
        ])

        if not run_commands_result.success:
            self.notifications.error('\tRestarting Dnsmasq failed')
            return run_commands_result.as_fail()

        self.notifications.success('\tRestarting Dnsmasq successful')

        return OperationResult[bool].succeed(True)
