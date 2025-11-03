"""Tests for DockerSetupGiteaAdminWindowsConfigurationTask.

This module contains unit tests for the Gitea administrator setup configuration
task on Windows systems, verifying that it correctly returns an unsupported error.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.docker_setup_gitea_admin import (
    DockerSetupGiteaAdminWindowsConfigurationTask,
)


class TestDockerSetupGiteaAdminWindowsConfigurationTask(unittest.TestCase):
    """Test suite for DockerSetupGiteaAdminWindowsConfigurationTask.

    Tests verify that the configuration task correctly returns an unsupported
    error when invoked on Windows systems.
    """

    task: DockerSetupGiteaAdminWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.task = DockerSetupGiteaAdminWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Test that the task returns 'Not supported' error on Windows."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
