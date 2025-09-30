from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.configuration.configuration_content_reader import ConfigurationContentReaderServiceContract
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class AutostartUbuntuConfigurationTask(ConfigurationTask):
    def __init__(self, reader: ConfigurationContentReaderServiceContract,
                 file_system: FileSystemServiceContract,
                 notifications: NotificationsServiceContract,
                 controller: PackageControllerServiceContract):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info('Configuring autostart script')
        autostart_data_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f'/usr/local/share/{data.server_data_dir}/data/autostart.service'
        )

        if not autostart_data_result.success or autostart_data_result.data == None:
            self.notifications.error(
                '\tFailed to read autostart service template'
            )
            return autostart_data_result.as_fail()
        self.notifications.success(
            '\tAutostart service template read successfully'
        )

        self.notifications.info(
            'Saving autostart configuration in the system.')
        write_result = self.file_system.write_text(
            '/etc/systemd/system/autostart.service',
            autostart_data_result.data
        )
        if not write_result.success:
            self.notifications.error(
                '\tFailed to save/overwrite autostart service'
            )
            return write_result.as_fail()

        self.notifications.success(
            '\tAutostart service configuration saved in the system successfully'
        )
        self.notifications.info('Enabling autostart service')
        run_result = self.controller.run_raw_commands([
            'sudo systemctl daemon-reload',
            'sudo systemctl enable autostart.service',
            'sudo systemctl start autostart.service'
        ])

        if not run_result.success:
            self.notifications.error(
                '\tFailed to enable autostart service'
            )
            return run_result.as_fail()
        self.notifications.success(
            '\tAutostart service enabled successfully'
        )

        return OperationResult[bool].succeed(True)
