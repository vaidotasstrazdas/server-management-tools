"""Tests for NftablesUbuntuConfigurationTask.

Verifies nftables firewall configuration on Ubuntu.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.nftables import (
    NftablesUbuntuConfigurationTask,
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


class TestNftablesUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for NftablesUbuntuConfigurationTask.

    Tests nftables setup including rules reading, validation, and service enablement.
    """

    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: NftablesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = NftablesUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"
        self.reader.read_result = OperationResult[str].succeed("nftables-config-result")
        self.maxDiff = None

    def test_happy_path(self):
        """Verify successful nftables configuration."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_results_in_correct_notifications_flow(self):
        """Verify correct notification sequence on success."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Nftables Config template data.", "type": "info"},
                {"text": "\tHost-fw rules read successfully.", "type": "success"},
                {"text": "Writing nftables configuration files.", "type": "info"},
                {"text": "\tNftables files written.", "type": "success"},
                {"text": "Applying sysctl/module settings.", "type": "info"},
                {"text": "\tApplying sysctl/module settings succeeded.", "type": "success"},
                {"text": "Setting iptables alternatives.", "type": "info"},
                {"text": "\tSetting iptables alternatives succeeded.", "type": "success"},
                {"text": "\tLoading nft rules.", "type": "info"},
                {"text": "\tLoading nft rules succeeded.", "type": "success"},
                {"text": "\tNftables configured successfully (Docker-safe).", "type": "success"},
            ],
        )

    def test_reads_config_using_correct_parameters(self):
        """Verify firewall rules read with correct path."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/nftables.d/10-host-fw.nft",
                )
            ],
        )

    def test_read_failure_results_in_task_failure(self):
        """Verify task fails when rules read fails."""
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_read_failure_results_in_correct_notifications_flow(self):
        """Verify notifications on rules read failure."""
        # Arrange
        fail_result = OperationResult[str].fail("Failure")
        self.reader.read_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Nftables Config template data.", "type": "info"},
                {"text": "\tReading host-fw rules failed.", "type": "error"},
            ],
        )

    def test_writes_config_using_correct_parameters(self):
        """Verify nftables.conf and rules files written correctly."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.file_system.write_text_params,
            [
                WriteTextParams(
                    path_location="/etc/nftables.conf",
                    text='#!/usr/sbin/nft -f\ninclude "/etc/nftables.d/*.nft"\n',
                ),
                WriteTextParams(
                    path_location="/etc/nftables.d/10-host-fw.nft", text="nftables-config-result"
                ),
            ],
        )

    def test_write_failure_result_in_task_failure(self):
        """Verify task fails when config file write fails."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_write_failure_result_in_correct_notifications_flow(self):
        """Verify notifications on config write failure."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Nftables Config template data.", "type": "info"},
                {"text": "\tHost-fw rules read successfully.", "type": "success"},
                {"text": "Writing nftables configuration files.", "type": "info"},
                {"text": "\tWriting /etc/nftables.conf failed.", "type": "error"},
            ],
        )

    def test_runs_correct_commands(self):
        """Verify sysctl, iptables-nft, and nft commands executed."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                ["sudo install -d -m 0755 /etc/nftables.d"],
                [
                    'echo "br_netfilter" | sudo tee /etc/modules-load.d/br_netfilter.conf '
                    ">/dev/null",
                    'echo "net.bridge.bridge-nf-call-iptables = 1" | sudo tee '
                    "/etc/sysctl.d/99-bridge-nf.conf >/dev/null",
                    'echo "net.ipv4.ip_forward = 1"               | sudo tee '
                    "/etc/sysctl.d/99-ipforward.conf   >/dev/null",
                    "sudo modprobe br_netfilter || true",
                    "sudo sysctl --system",
                ],
                [
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "
                    "--no-install-recommends iptables nftables",
                    "sudo update-alternatives --set iptables   /usr/sbin/iptables-nft",
                    "sudo update-alternatives --set ip6tables  /usr/sbin/ip6tables-nft",
                    "sudo update-alternatives --set arptables  /usr/sbin/arptables-nft",
                    "sudo update-alternatives --set ebtables   /usr/sbin/ebtables-nft",
                ],
                [
                    'sudo nft list tables | grep -q "table inet host_fw" && sudo nft delete '
                    "table inet host_fw || true",
                    "sudo nft -c -f /etc/nftables.d/10-host-fw.nft",
                    "sudo nft -f /etc/nftables.d/10-host-fw.nft",
                    "sudo systemctl enable nftables",
                    "sudo ufw disable || true",
                ],
            ],
        )

    def test_running_commands_failure_results_in_task_failure(self):
        """Verify task fails when commands fail."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, fail_result)

    def test_running_commands_failure_results_in_correct_notifications_flow(self):
        """Verify notifications on command execution failure."""
        # Arrange
        fail_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = fail_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Reading Nftables Config template data.", "type": "info"},
                {"text": "\tHost-fw rules read successfully.", "type": "success"},
                {"text": "Writing nftables configuration files.", "type": "info"},
                {"text": "\tCreating /etc/nftables.d failed.", "type": "error"},
            ],
        )
