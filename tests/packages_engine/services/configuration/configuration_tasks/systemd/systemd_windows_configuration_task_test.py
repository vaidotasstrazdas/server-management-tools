"""Tests for SystemdWindowsConfigurationTask. Verifies unsupported platform handling."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.systemd import (
    SystemdWindowsConfigurationTask,
)


class TestSystemdWindowsConfigurationTask(unittest.TestCase):
    """Test suite for SystemdWindowsConfigurationTask. Tests Windows platform rejection."""

    task: SystemdWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = SystemdWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verifies task returns unsupported error on Windows platform."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
