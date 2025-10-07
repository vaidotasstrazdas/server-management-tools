"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.docker import DockerWindowsInstallerTask


class TestDockerWindowsInstallerTask(unittest.TestCase):
    """Docker Windows Installer Task Tests."""

    task: DockerWindowsInstallerTask

    def setUp(self):
        self.task = DockerWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
