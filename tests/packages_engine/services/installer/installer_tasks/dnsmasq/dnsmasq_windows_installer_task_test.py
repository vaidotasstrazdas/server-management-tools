"""Necessary imports for the tests."""
import unittest
from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.dnsmasq import DnsmasqWindowsInstallerTask


class TestDnsmasqWindowsInstallerTask(unittest.TestCase):
    """Dnsmasw Windows Installer Task tests."""
    task: DnsmasqWindowsInstallerTask

    def setUp(self):
        self.task = DnsmasqWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))
