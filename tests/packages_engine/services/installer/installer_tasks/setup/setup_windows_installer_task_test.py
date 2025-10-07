"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.setup import (
    SetupWindowsInstallerTask,
)


class TestSetupWindowsInstallerTask(unittest.TestCase):
    """Tests for the Windows installer task."""

    task: SetupWindowsInstallerTask

    def setUp(self):
        self.task = SetupWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
