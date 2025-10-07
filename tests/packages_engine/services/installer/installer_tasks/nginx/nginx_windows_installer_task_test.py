"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.nginx import NginxWindowsInstallerTask


class TestNginxWindowsInstallerTask(unittest.TestCase):
    """Nginx Windows Installer Task Tests."""

    task: NginxWindowsInstallerTask

    def setUp(self):
        self.task = NginxWindowsInstallerTask()

    def test_returns_unsupported_error(self):
        """Returns unsupported error."""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
