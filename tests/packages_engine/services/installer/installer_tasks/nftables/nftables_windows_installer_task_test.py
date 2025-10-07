"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.nftables import NftablesWindowsInstallerTask


class TestNftablesWindowsInstallerTask(unittest.TestCase):
    """Nftables Windows Installer Task Tests."""

    task: NftablesWindowsInstallerTask

    def setUp(self):
        self.task = NftablesWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
