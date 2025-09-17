import unittest

from packages_engine.models import OperationResult

from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import MockSystemManagementEngineService
from packages_engine.services.installer.installer_tasks.nftables import NftablesUbuntuInstallerTask

class TestNftablesUbuntuInstallerTask(unittest.TestCase):
    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: NftablesUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = NftablesUbuntuInstallerTask(self.notifications, self.engine, self.controller)
    
    def test_checks_for_nftables_installation_status(self):
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ['nftables'])

    def test_notification_flow_when_nftables_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Nftables will be installed now if it is not installed.'},
                {'type':'success','text':'\tNftables is installed already. Nothing needs to be done.'},
            ]
        )

    def test_notification_flow_when_nftables_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Nftables will be installed now if it is not installed.'}
            ]
        )

    def test_no_commands_executed_when_nftables_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_nftables_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(
            params,
            [
                [
                    'sudo apt update',
                    'sudo apt install -y nftables',
                    'sudo systemctl enable --now nftables'
                ]
            ]
        )

    def test_returns_result_from_packages_controller_when_nftables_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = OperationResult[bool].succeed(True)

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_nftables_installed(self):
        # Arrange
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = OperationResult[bool].fail('failure')

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))