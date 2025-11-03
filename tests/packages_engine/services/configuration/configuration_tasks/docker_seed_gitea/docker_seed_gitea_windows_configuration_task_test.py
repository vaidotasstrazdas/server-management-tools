"""Tests for DockerSeedGiteaWindowsConfigurationTask.

Verifies Windows platform returns unsupported status for Gitea seeding.
"""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.docker_seed_gitea import (
    DockerSeedGiteaWindowsConfigurationTask,
)


class TestDockerSeedGiteaWindowsConfigurationTask(unittest.TestCase):
    """Test suite for DockerSeedGiteaWindowsConfigurationTask.

    Tests that Windows Gitea seeding configuration is not yet implemented.
    """

    task: DockerSeedGiteaWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.task = DockerSeedGiteaWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        """Verifies task returns unsupported error on Windows platform."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
