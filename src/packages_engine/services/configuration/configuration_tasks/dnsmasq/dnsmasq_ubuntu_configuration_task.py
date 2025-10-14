from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class DnsmasqUbuntuConfigurationTask(ConfigurationTask):
    """Dnsmasq configuration task."""

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
        self.notifications.info("Reading Dnsmasq Config template data.")
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/dnsmasq.conf",
        )
        if not read_result.success or read_result.data is None:
            self.notifications.error("\tReading Dnsmasq Config template data failed.")
            return read_result.as_fail()
        self.notifications.success("\tReading Dnsmasq Config template data successful.")
        self.notifications.info(
            f"\tWill configure using the following configuration:\n\n{read_result.data}"
        )

        self.notifications.info("Writing Dnsmasq Config data.")
        mk_res = self.controller.run_raw_commands(["sudo install -d -m 0755 /etc/dnsmasq.d"])
        if not mk_res.success:
            self.notifications.error("\tCreating /etc/dnsmasq.d failed.")
            return mk_res.as_fail()

        write_res = self.file_system.write_text("/etc/dnsmasq.d/internal.conf", read_result.data)
        if not write_res.success:
            self.notifications.error("\tWriting Dnsmasq Config data failed.")
            return write_res.as_fail()
        self.notifications.success("\tWriting Dnsmasq Config data successful.")

        self.notifications.info("Validating Dnsmasq configuration.")
        test_res = self.controller.run_raw_commands(["sudo dnsmasq --test"])
        if not test_res.success:
            self.notifications.error("\tDnsmasq config test failed.")
            return test_res.as_fail()
        self.notifications.success("\tDnsmasq config test OK.")

        self.notifications.info(
            "Configuration Dnsmasq configuration permissions, enabling and (re)starting Dnsmasq."
        )
        run_res = self.controller.run_raw_commands(
            [
                "sudo chown root:root /etc/dnsmasq.d/internal.conf",
                "sudo chmod 0644 /etc/dnsmasq.d/internal.conf",
                "sudo systemctl reset-failed dnsmasq || true",
                "sudo systemctl enable --now dnsmasq",
                "sudo install -d -m 0755 /etc/systemd/system/dnsmasq.service.d",
                "sudo bash -lc 'cat > /etc/systemd/system/dnsmasq.service.d/10-after-wg0.conf <<EOF\n[Unit]\nAfter=wg-quick@wg0.service\nWants=wg-quick@wg0.service\nEOF'",
                "sudo systemctl daemon-reload",
                "sudo systemctl reload-or-restart dnsmasq",
            ]
        )
        if not run_res.success:
            self.notifications.error("\tRunning Dnsmasq failed.")
            return run_res.as_fail()
        self.notifications.success("\tDnsmasq running with new configuration.")

        return OperationResult[bool].succeed(True)
