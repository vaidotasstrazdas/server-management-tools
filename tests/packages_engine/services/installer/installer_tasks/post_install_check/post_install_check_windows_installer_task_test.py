"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.post_install_check import (
    PostInstallCheckWindowsInstallerTask,
)


class TestPostInstallCheckWindowsInstallerTask(unittest.TestCase):
    """Tests for the Windows installer task."""

    task: PostInstallCheckWindowsInstallerTask

    def setUp(self):
        self.task = PostInstallCheckWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
