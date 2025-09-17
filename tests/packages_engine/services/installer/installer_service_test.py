import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer import InstallerService
from packages_engine.services.installer.installer_tasks.installer_task_mock import MockInstallerTask

class TestInstallerService(unittest.TestCase):
    service: InstallerService
    taskOne: MockInstallerTask
    taskTwo: MockInstallerTask

    def setUp(self):
        self.service = InstallerService()
        self.taskOne = MockInstallerTask()
        self.taskTwo = MockInstallerTask()
    
    def test_executes_installer_tasks(self):
        # Act
        self.service.install([self.taskOne, self.taskTwo])

        # Assert
        self.assertEqual(self.taskOne.install_triggered_times, 1)
        self.assertEqual(self.taskTwo.install_triggered_times, 1)
    
    def test_stops_executing_other_tasks_when_one_fails(self):
        # Arrange
        self.taskOne.install_result = OperationResult[bool].fail('failure')

        # Act
        self.service.install([self.taskOne, self.taskTwo])

        # Assert
        self.assertEqual(self.taskOne.install_triggered_times, 1)
        self.assertEqual(self.taskTwo.install_triggered_times, 0)
    
    def test_returns_result_of_first_failed_task_on_failure(self):
        # Arrange
        taskThree = MockInstallerTask()
        self.taskTwo.install_result = OperationResult[bool].fail('failure 1')
        taskThree.install_result = OperationResult[bool].fail('failure 2')
        
        # Act
        result = self.service.install([self.taskOne, self.taskTwo, taskThree])

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('failure 1'))
    
    def test_returns_result_success_when_all_tasks_succeed(self):
        # Act
        result = self.service.install([self.taskOne, self.taskTwo])

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))