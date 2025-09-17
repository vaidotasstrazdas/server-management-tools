import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.nftables import NftablesWindowsInstallerTask

class TestNftablesWindowsInstallerTask(unittest.TestCase):
    task: NftablesWindowsInstallerTask

    def setUp(self):
        self.task = NftablesWindowsInstallerTask()
    
    def test_returns_unsupported_error(self):
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))