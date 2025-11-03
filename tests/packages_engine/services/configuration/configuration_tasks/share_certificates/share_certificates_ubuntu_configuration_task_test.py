"""Tests for ShareCertificatesUbuntuConfigurationTask.

Verifies CA certificate sharing to client devices on Ubuntu.
"""
import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_tasks.share_certificates import (
    ShareCertificatesUbuntuConfigurationTask,
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


class TestShareCertificatesUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for ShareCertificatesUbuntuConfigurationTask.

    Tests CA certificate reading and copying to client data directory.
    """
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: ShareCertificatesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = ShareCertificatesUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.clients_data_dir = "/dev/usb"

        self.file_system.read_text_result_map = {
            "/etc/ssl/internal-pki/ca.crt": OperationResult[str].succeed("ca-data")
        }

        self.file_system.write_text_result_map = {
            "/dev/usb/certificate.crt": OperationResult[bool].succeed(True),
        }

        self.maxDiff = None

    def test_happy_path(self):
        """Verify successful certificate sharing."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        """Verify correct notification sequence during successful sharing."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing Certificates for the users.", "type": "info"},
                {"text": "Reading certificates configuration.", "type": "info"},
                {"text": "Reading certificates configuration successful.", "type": "success"},
                {"text": "Sharing certificates configuration with clients.", "type": "info"},
                {
                    "text": "Sharing certificates configuration with clients successful.",
                    "type": "success",
                },
            ],
        )

    def test_reads_certificate_data(self):
        """Verify CA certificate is read from correct path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(self.file_system.read_text_params, ["/etc/ssl/internal-pki/ca.crt"])

    def test_failure_to_read_certificates_data_results_in_failure(self):
        """Verify task fails when CA certificate cannot be read."""
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.file_system.read_text_result_map = {"/etc/ssl/internal-pki/ca.crt": failure_result}

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_certificates_data_results_in_failure_notifications_flow(self):
        """Verify error notifications when CA certificate read fails."""
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.file_system.read_text_result_map = {"/etc/ssl/internal-pki/ca.crt": failure_result}

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing Certificates for the users.", "type": "info"},
                {"text": "Reading certificates configuration.", "type": "info"},
                {"text": "Reading certificates configuration failed.", "type": "error"},
            ],
        )

    def test_stores_certificate_data(self):
        """Verify CA certificate is written to client data directory."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [WriteTextParams("/dev/usb/certificate.crt", "ca-data")],
        )

    def test_failure_to_store_certificate_data_results_in_failure(self):
        """Verify task fails when CA certificate cannot be written."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map = {"/dev/usb/certificate.crt": failure_result}

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_certificate_data_results_in_failure_notifications_flow(self):
        """Verify error notifications when CA certificate write fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map = {"/dev/usb/certificate.crt": failure_result}

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Sharing Certificates for the users.", "type": "info"},
                {"text": "Reading certificates configuration.", "type": "info"},
                {"text": "Reading certificates configuration successful.", "type": "success"},
                {"text": "Sharing certificates configuration with clients.", "type": "info"},
                {
                    "text": "Sharing certificates configuration with clients failed.",
                    "type": "error",
                },
            ],
        )
