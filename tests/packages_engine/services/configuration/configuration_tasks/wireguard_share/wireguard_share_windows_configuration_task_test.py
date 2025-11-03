"""Tests for WireguardShareWindowsConfigurationTask.

Verifies Windows platform returns unsupported status.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.wireguard_share import (
    WireguardShareWindowsConfigurationTask,
)


class TestWireguardShareWindowsConfigurationTask(unittest.TestCase):
    """Test suite for WireguardShareWindowsConfigurationTask.

    Tests that Windows implementation properly returns unsupported status.
    """

    task: WireguardShareWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = WireguardShareWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verify task returns unsupported error on Windows."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
