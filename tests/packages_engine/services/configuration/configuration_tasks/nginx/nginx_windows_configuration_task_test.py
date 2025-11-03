"""Tests for NginxWindowsConfigurationTask. Verifies unsupported platform handling."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.nginx import (
    NginxWindowsConfigurationTask,
)


class TestNginxWindowsConfigurationTask(unittest.TestCase):
    """Test suite for NginxWindowsConfigurationTask. Tests Windows platform rejection."""

    task: NginxWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = NginxWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verifies task returns unsupported error on Windows platform."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
