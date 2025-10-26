import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.wireguard_peers import (
    WireguardPeersWindowsConfigurationTask,
)


class TestWireguardPeersWindowsConfigurationTask(unittest.TestCase):
    task: WireguardPeersWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = WireguardPeersWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
