"""Necessary imports for the tests."""

import unittest
from unittest.mock import patch

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import GenericInstallerTask
from packages_engine.services.installer.installer_tasks.installer_task_mock import MockInstallerTask

_PACKAGE_NAME = "packages_engine.services.installer.installer_tasks.generic_installer_task"


class TestGenericInstallerTask(unittest.TestCase):
    """Generic installer task tests."""

    mock_ubuntu_task: MockInstallerTask
    mock_windows_task: MockInstallerTask
    task: GenericInstallerTask

    def setUp(self):
        self.mock_ubuntu_task = MockInstallerTask()
        self.mock_windows_task = MockInstallerTask()
        self.task = GenericInstallerTask(self.mock_ubuntu_task, self.mock_windows_task)

    @patch(f"{_PACKAGE_NAME}.sys.platform", "linux")
    def test_runs_ubuntu_task_on_ubuntu_platform(self):
        """Runs Ubuntu task on Ubuntu platform."""
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mock_ubuntu_task.install_triggered_times, 1)
        self.assertEqual(self.mock_windows_task.install_triggered_times, 0)

    @patch(f"{_PACKAGE_NAME}.sys.platform", "win32")
    def test_runs_windows_task_on_windows_platform(self):
        """Runs Windows task on Windows platform."""
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mock_ubuntu_task.install_triggered_times, 0)
        self.assertEqual(self.mock_windows_task.install_triggered_times, 1)

    @patch(f"{_PACKAGE_NAME}.sys.platform", "unknown")
    def test_runs_no_task_on_unknown_platform(self):
        """Runs no task on unknown platform."""
        # Act
        self.task.install()

        # Assert
        self.assertEqual(self.mock_ubuntu_task.install_triggered_times, 0)
        self.assertEqual(self.mock_windows_task.install_triggered_times, 0)

    @patch(f"{_PACKAGE_NAME}.sys.platform", "unknown")
    def test_returns_failure_on_unknown_platform(self):
        """Returns failure on unknown platform"""
        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported platform "unknown"'))

    @patch(f"{_PACKAGE_NAME}.sys.platform", "linux")
    def test_returns_ubuntu_result_on_ubuntu_platform(self):
        """Returns Ubuntu result on Ubuntu platform."""
        # Arrange
        self.mock_ubuntu_task.install_result = OperationResult[bool].succeed(True)
        self.mock_windows_task.install_result = OperationResult[bool].fail("failed")

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.mock_ubuntu_task.install_result)

    @patch(f"{_PACKAGE_NAME}.sys.platform", "windows")
    def test_returns_windows_result_on_windows_platform(self):
        """Returns Windows result on Windows platform."""
        # Arrange
        self.mock_ubuntu_task.install_result = OperationResult[bool].succeed(True)
        self.mock_windows_task.install_result = OperationResult[bool].fail("failed")

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.mock_windows_task.install_result)
