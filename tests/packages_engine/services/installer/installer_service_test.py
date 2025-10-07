"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer import InstallerService
from packages_engine.services.installer.installer_tasks.installer_task_mock import MockInstallerTask


class TestInstallerService(unittest.TestCase):
    """Installer service tests."""

    service: InstallerService
    task_one: MockInstallerTask
    task_two: MockInstallerTask

    def setUp(self):
        self.service = InstallerService()
        self.task_one = MockInstallerTask()
        self.task_two = MockInstallerTask()

    def test_executes_installer_tasks(self):
        """Executes installer tasks."""
        # Act
        self.service.install([self.task_one, self.task_two])

        # Assert
        self.assertEqual(self.task_one.install_triggered_times, 1)
        self.assertEqual(self.task_two.install_triggered_times, 1)

    def test_stops_executing_other_tasks_when_one_fails(self):
        """Stops executijng other tasks when one fails."""
        # Arrange
        self.task_one.install_result = OperationResult[bool].fail("failure")

        # Act
        self.service.install([self.task_one, self.task_two])

        # Assert
        self.assertEqual(self.task_one.install_triggered_times, 1)
        self.assertEqual(self.task_two.install_triggered_times, 0)

    def test_returns_result_of_first_failed_task_on_failure(self):
        """Returns result of first failed task on failure."""
        # Arrange
        task_three = MockInstallerTask()
        self.task_two.install_result = OperationResult[bool].fail("failure 1")
        task_three.install_result = OperationResult[bool].fail("failure 2")

        # Act
        result = self.service.install([self.task_one, self.task_two, task_three])

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("failure 1"))

    def test_returns_result_success_when_all_tasks_succeed(self):
        """Returns result success when all tasks succeed."""
        # Act
        result = self.service.install([self.task_one, self.task_two])

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))
