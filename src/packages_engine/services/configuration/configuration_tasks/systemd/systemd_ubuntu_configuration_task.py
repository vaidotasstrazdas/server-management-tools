from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class SystemdUbuntuConfigurationTask(ConfigurationTask):
    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info("Will configure systemd now.")

        self.notifications.info("Reading split DNS configuration.")
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/systemd/resolved.conf.d/10-wg-split-dns.conf",
        )
        if not read_result.success or read_result.data is None:
            self.notifications.error("Reading split DNS configuration failed.")
            return read_result.as_fail()
        self.notifications.success("Reading split DNS configuration successful.")

        self.notifications.info("Writing split DNS configuration data.")
        mk_res = self.controller.run_raw_commands(
            ["sudo install -d -m 0755 /etc/systemd/resolved.conf.d"]
        )
        if not mk_res.success:
            self.notifications.error("\tFailed installing /etc/systemd/resolved.conf.d.")
            return mk_res.as_fail()
        self.notifications.success("\tInstalling /etc/systemd/resolved.conf.d successful.")

        write_res = self.file_system.write_text(
            "/etc/systemd/resolved.conf.d/10-wg-split-dns.conf", read_result.data
        )
        if not write_res.success:
            self.notifications.error("\tWriting split DNS config data failed.")
            return write_res.as_fail()
        self.notifications.success("\tWriting split DNS config data successful.")

        self.notifications.info(
            "Configuration split DNS configuration permissions, restarting system."
        )
        run_res = self.controller.run_raw_commands(
            [
                "sudo chown root:root /etc/systemd/resolved.conf.d/10-wg-split-dns.conf",
                "sudo chmod 0644 /etc/systemd/resolved.conf.d/10-wg-split-dns.conf",
                "sudo systemctl reload-or-restart systemd-resolved",
            ]
        )
        if not run_res.success:
            self.notifications.error("\tRunning systemd configuration failed.")
            return run_res.as_fail()
        self.notifications.success("\tsystemd running with new configuration.")

        return OperationResult[bool].succeed(True)
