import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.dnsmasq import DnsmasqWindowsInstallerTask

class TestDnsmasqWindowsInstallerTask(unittest.TestCase):
    task: DnsmasqWindowsInstallerTask

    def setUp(self):
        self.task = DnsmasqWindowsInstallerTask()
    
    def test_returns_unsupported_error(self):
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))