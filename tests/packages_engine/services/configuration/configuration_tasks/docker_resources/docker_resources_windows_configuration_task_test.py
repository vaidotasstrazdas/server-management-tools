"""Tests for DockerResourcesWindowsConfigurationTask. Validates Windows platform is unsupported."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.docker_resources import (
    DockerResourcesWindowsConfigurationTask,
)


class TestDockerResourcesWindowsConfigurationTask(unittest.TestCase):
    """Test suite for DockerResourcesWindowsConfigurationTask. Confirms Windows resource setup returns not supported error."""

    task: DockerResourcesWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = DockerResourcesWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verifies configuration returns not supported error on Windows."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
