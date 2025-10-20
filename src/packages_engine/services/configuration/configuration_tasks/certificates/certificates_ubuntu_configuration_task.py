from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class CertificatesUbuntuConfigurationTask(ConfigurationTask):
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
        self.notifications.info("Configuring certificates if needed")
        process_result = self._process_paths(
            [
                "/etc/ssl/internal-pki",
                "/etc/ssl/internal-pki/san.cnf",
                f"/etc/ssl/internal-pki/{data.domain_name}.key",
                f"/etc/ssl/internal-pki/{data.domain_name}.csr",
                f"/etc/ssl/internal-pki/{data.domain_name}.crt",
                "/etc/ssl/certs/internal.crt",
                "/etc/ssl/private/internal.key",
            ]
        )

        if not process_result.success or process_result.data is None:
            return process_result.as_fail()

        if process_result.data is True:
            self.notifications.success("\tPKI configured already. Nothing needs to be done.")
            return OperationResult[bool].succeed(True)

        self.notifications.info("Reading SSL configuration template.")
        ssl_read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/ssl.conf",
        )
        if not ssl_read_result.success or ssl_read_result.data is None:
            self.notifications.error("\tFailed to read SSL configuration.")
            return ssl_read_result.as_fail()
        self.notifications.success("\tSSL Configuration template read successfull.")

        self.notifications.info("Saving SSL configuration.")
        write_result = self.file_system.write_text(
            "/etc/ssl/internal-pki/san.cnf", ssl_read_result.data
        )
        if not write_result.success:
            self.notifications.error("\tSaving SSL configuration failed.")
            return write_result.as_fail()
        self.notifications.success("\tSSL Configuration saved successfully.")

        self.notifications.info("Running commands to create private and public keys if needed.")
        run_result = self.controller.run_raw_commands(
            [
                "mkdir -p /etc/ssl/internal-pki",
                "mkdir -p /etc/ssl/certs",
                "mkdir -p /etc/ssl/private",
                "cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096",
                'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt',
                f"cd /etc/ssl/internal-pki && sudo openssl genrsa -out {data.domain_name}.key 2048",
                f"cd /etc/ssl/internal-pki && sudo openssl req -new -key {data.domain_name}.key -out {data.domain_name}.csr -config san.cnf",
                f"cd /etc/ssl/internal-pki && sudo openssl x509 -req -in {data.domain_name}.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out {data.domain_name}.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf",
                f"sudo cp /etc/ssl/internal-pki/{data.domain_name}.crt /etc/ssl/certs/internal.crt",
                f"sudo cp /etc/ssl/internal-pki/{data.domain_name}.key /etc/ssl/private/internal.key",
                "sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key",
                "sudo chmod 644 /etc/ssl/certs/internal.crt",
                "sudo chmod 600 /etc/ssl/private/internal.key",
            ]
        )

        if not run_result.success:
            self.notifications.error("\tCommands failed.")
            return run_result.as_fail()
        self.notifications.success("\tCommands succeeded.")

        return OperationResult[bool].succeed(True)

    def _process_paths(self, paths: list[str]) -> OperationResult[bool]:
        config_created = True
        self.notifications.info("Checking if PKI is configured")
        for path in paths:
            if not self.file_system.path_exists(path):
                config_created = False
                break

        if not config_created:
            self.notifications.info("\tPKI is not configured. Will remove unnecessary files")
            for path in paths:
                if self.file_system.path_exists(path):
                    self.notifications.info(f'\tRemoving "{path}"')
                    remove_result = self.file_system.remove_location(path)
                    if not remove_result.success:
                        self.notifications.error(f'\t\tRemoving "{path}" failed')
                        return remove_result.as_fail()
                    self.notifications.success(f'\t\tRemoving "{path}" successful')
        else:
            self.notifications.info("\tPKI is configured")

        return OperationResult[bool].succeed(config_created)
