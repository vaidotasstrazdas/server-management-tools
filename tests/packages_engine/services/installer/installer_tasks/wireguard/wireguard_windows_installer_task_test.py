import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.wireguard import WireguardWindowsInstallerTask

class TestWireguardWindowsInstallerTask(unittest.TestCase):
    task: WireguardWindowsInstallerTask

    def setUp(self):
        self.task = WireguardWindowsInstallerTask()
    
    def test_returns_unsupported_error(self):
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))