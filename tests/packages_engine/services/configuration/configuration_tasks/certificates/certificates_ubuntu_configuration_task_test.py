import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.certificates import (
    CertificatesUbuntuConfigurationTask,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
    WriteTextParams,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestCertificatesUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: CertificatesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = CertificatesUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"

        self.file_system.write_text_result_map = {
            "/etc/ssl/internal-pki/san.cnf": OperationResult[bool].succeed(True),
        }

        self.reader.read_result = OperationResult[str].succeed("ssl-configuration")
        self.maxDiff = None

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tSSL Configuration template read successfull.", "type": "success"},
                {"text": "Ensuring PKI folders and permissions.", "type": "info"},
                {"text": "Ensuring PKI folders and permissions succeeded.", "type": "success"},
                {"text": "(Re)writing SAN template.", "type": "info"},
                {"text": "(Re)writing SAN template successful.", "type": "success"},
                {"text": "Creating CA if missing (idempotent).", "type": "info"},
                {"text": "Creating CA succeeded.", "type": "success"},
                {"text": "Creating server key/cert if missing (idempotent).", "type": "info"},
                {"text": "Creating server key/cert succeeded.", "type": "success"},
                {"text": "\tCertificates ready.", "type": "success"},
            ],
        )

    def test_reads_san_template(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING, self.data, "/usr/local/share/srv/data/ssl.conf"
                )
            ],
        )

    def test_failure_to_read_san_template_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_san_template_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tFailed to read SSL configuration.", "type": "error"},
            ],
        )

    def test_runs_correct_commands(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    "sudo install -d -m 0700 -o root -g root /etc/ssl/internal-pki",
                    "sudo install -d -m 0755 -o root -g root /etc/ssl/certs",
                    "sudo install -d -m 0700 -o root -g root /etc/ssl/private",
                ],
                [
                    "test -f /etc/ssl/internal-pki/ca.key || (umask 077 && openssl genrsa -out "
                    "/etc/ssl/internal-pki/ca.key 4096)",
                    "test -f /etc/ssl/internal-pki/ca.crt || openssl req -x509 -new -sha256 "
                    '-days 3650 -key /etc/ssl/internal-pki/ca.key -subj "/CN=Internal VPN CA" '
                    "-out /etc/ssl/internal-pki/ca.crt",
                    "sudo chmod 600 /etc/ssl/internal-pki/ca.key",
                ],
                [
                    "test -f /etc/ssl/internal-pki/.key || (umask 077 && openssl genrsa -out "
                    "/etc/ssl/internal-pki/.key 2048)",
                    "test -f /etc/ssl/internal-pki/.csr || openssl req -new -key "
                    "/etc/ssl/internal-pki/.key -out /etc/ssl/internal-pki/.csr -config "
                    "/etc/ssl/internal-pki/san.cnf",
                    "test -f /etc/ssl/internal-pki/.crt || openssl x509 -req -in "
                    "/etc/ssl/internal-pki/.csr -CA /etc/ssl/internal-pki/ca.crt -CAkey "
                    "/etc/ssl/internal-pki/ca.key -CAcreateserial -out "
                    "/etc/ssl/internal-pki/.crt -days 825 -sha256 -extensions req_ext -extfile "
                    "/etc/ssl/internal-pki/san.cnf",
                    "sudo install -m 0644 -o root -g root /etc/ssl/internal-pki/.crt "
                    "/etc/ssl/certs/internal.crt",
                    "sudo install -m 0600 -o root -g root /etc/ssl/internal-pki/.key "
                    "/etc/ssl/private/internal.key",
                ],
            ],
        )

    def test_pki_folders_ensurance_command_failure_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0700 -o root -g root /etc/ssl/internal-pki"
        ] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_pki_folders_ensurance_command_failure_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "sudo install -d -m 0700 -o root -g root /etc/ssl/internal-pki"
        ] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tSSL Configuration template read successfull.", "type": "success"},
                {"text": "Ensuring PKI folders and permissions.", "type": "info"},
                {"text": "Ensuring PKI folders and permissions failed.", "type": "error"},
            ],
        )

    def test_keygen_command_failure_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "test -f /etc/ssl/internal-pki/ca.key || (umask 077 && openssl genrsa -out"
        ] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_keygen_command_failure_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map[
            "test -f /etc/ssl/internal-pki/ca.key || (umask 077 && openssl genrsa -out"
        ] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tSSL Configuration template read successfull.", "type": "success"},
                {"text": "Ensuring PKI folders and permissions.", "type": "info"},
                {"text": "Ensuring PKI folders and permissions succeeded.", "type": "success"},
                {"text": "(Re)writing SAN template.", "type": "info"},
                {"text": "(Re)writing SAN template successful.", "type": "success"},
                {"text": "Creating CA if missing (idempotent).", "type": "info"},
                {"text": "Creating CA failed.", "type": "error"},
            ],
        )

    def test_keycert_command_failure_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["test -f /etc/ssl/internal-pki/.key"] = (
            failure_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_keycert_command_failure_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result_regex_map["test -f /etc/ssl/internal-pki/.key"] = (
            failure_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tSSL Configuration template read successfull.", "type": "success"},
                {"text": "Ensuring PKI folders and permissions.", "type": "info"},
                {"text": "Ensuring PKI folders and permissions succeeded.", "type": "success"},
                {"text": "(Re)writing SAN template.", "type": "info"},
                {"text": "(Re)writing SAN template successful.", "type": "success"},
                {"text": "Creating CA if missing (idempotent).", "type": "info"},
                {"text": "Creating CA succeeded.", "type": "success"},
                {"text": "Creating server key/cert if missing (idempotent).", "type": "info"},
                {"text": "Creating server key/cert failed.", "type": "error"},
            ],
        )

    def test_stores_san_template(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/etc/ssl/internal-pki/san.cnf", "ssl-configuration")],
        )

    def test_failure_to_store_san_template_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map = {
            "/etc/ssl/internal-pki/san.cnf": failure_result,
        }

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_san_template_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map = {
            "/etc/ssl/internal-pki/san.cnf": failure_result,
        }

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring certificates if needed", "type": "info"},
                {"text": "Reading SSL configuration template.", "type": "info"},
                {"text": "\tSSL Configuration template read successfull.", "type": "success"},
                {"text": "Ensuring PKI folders and permissions.", "type": "info"},
                {"text": "Ensuring PKI folders and permissions succeeded.", "type": "success"},
                {"text": "(Re)writing SAN template.", "type": "info"},
                {"text": "(Re)writing SAN template failed.", "type": "error"},
            ],
        )
