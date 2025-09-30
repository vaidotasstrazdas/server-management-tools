import unittest

from packages_engine.services.installer.installer_service_mock import MockInstallerService
from packages_engine.services.installer.installer_tasks.installer_task_mock import MockInstallerTask
from packages_engine.commands import InstallCommand


class TestInstallCommand(unittest.TestCase):
    service: MockInstallerService
    task_one: MockInstallerTask
    task_two: MockInstallerTask
    command: InstallCommand

    def setUp(self):
        self.service = MockInstallerService()
        self.task_one = MockInstallerTask()
        self.task_two = MockInstallerTask()
        self.command = InstallCommand(
            self.service, [self.task_one, self.task_two]
        )

    def test_executes_configured_tasks(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.service.install_params,
            [[self.task_one, self.task_two]]
        )
