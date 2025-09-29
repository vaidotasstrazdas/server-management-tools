import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks.dnsmasq import DnsmasqWindowsConfigurationTask

class TestDnsmasqWindowsConfigurationTask(unittest.TestCase):
    task: DnsmasqWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = DnsmasqWindowsConfigurationTask()
        self.data = ConfigurationData.default()
    
    def test_returns_unsupported_error(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))