"""Tests for NftablesWindowsConfigurationTask.

Verifies Windows nftables configuration returns unsupported status.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.nftables import (
    NftablesWindowsConfigurationTask,
)


class TestNftablesWindowsConfigurationTask(unittest.TestCase):
    """Test suite for NftablesWindowsConfigurationTask.

    Tests that Windows nftables configuration is not yet implemented.
    """

    task: NftablesWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = NftablesWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verify task returns 'Not supported' error."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
