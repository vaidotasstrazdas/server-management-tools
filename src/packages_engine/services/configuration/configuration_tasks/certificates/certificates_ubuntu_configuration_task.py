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

        self.notifications.info("Ensuring PKI folders and permissions.")
        cmds = [
            "sudo install -d -m 0700 -o root -g root /etc/ssl/internal-pki",
            "sudo install -d -m 0755 -o root -g root /etc/ssl/certs",
            "sudo install -d -m 0700 -o root -g root /etc/ssl/private",
        ]
        res = self.controller.run_raw_commands(cmds)
        if not res.success:
            return res.as_fail()

        # Always (re)write SAN template (safe)
        write_result = self.file_system.write_text(
            "/etc/ssl/internal-pki/san.cnf", ssl_read_result.data
        )
        if not write_result.success:
            return write_result.as_fail()

        domain = data.domain_name
        pki = "/etc/ssl/internal-pki"

        self.notifications.info("Creating CA if missing (idempotent).")
        res = self.controller.run_raw_commands(
            [
                f"test -f {pki}/ca.key || (umask 077 && openssl genrsa -out {pki}/ca.key 4096)",
                f'test -f {pki}/ca.crt || openssl req -x509 -new -sha256 -days 3650 -key {pki}/ca.key -subj "/CN=Internal VPN CA" -out {pki}/ca.crt',
                f"sudo chmod 600 {pki}/ca.key",
            ]
        )
        if not res.success:
            return res.as_fail()

        self.notifications.info("Creating server key/cert if missing (idempotent).")
        res = self.controller.run_raw_commands(
            [
                f"test -f {pki}/{domain}.key || (umask 077 && openssl genrsa -out {pki}/{domain}.key 2048)",
                f"test -f {pki}/{domain}.csr || openssl req -new -key {pki}/{domain}.key -out {pki}/{domain}.csr -config {pki}/san.cnf",
                f"test -f {pki}/{domain}.crt || openssl x509 -req -in {pki}/{domain}.csr -CA {pki}/ca.crt -CAkey {pki}/ca.key -CAcreateserial -out {pki}/{domain}.crt -days 825 -sha256 -extensions req_ext -extfile {pki}/san.cnf",
                f"sudo install -m 0644 -o root -g root {pki}/{domain}.crt /etc/ssl/certs/internal.crt",
                f"sudo install -m 0600 -o root -g root {pki}/{domain}.key /etc/ssl/private/internal.key",
            ]
        )

        if not res.success:
            return res.as_fail()

        self.notifications.success("\tCertificates ready.")

        return OperationResult[bool].succeed(True)
