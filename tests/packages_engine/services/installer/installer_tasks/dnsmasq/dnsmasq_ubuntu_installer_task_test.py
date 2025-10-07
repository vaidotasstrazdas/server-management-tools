"""Necessary imports for the tests."""
import unittest
from packages_engine.models import OperationResult
from packages_engine.services.\
    notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.\
    package_controller_service_mock import MockPackageControllerService
from packages_engine.services.system_management_engine.\
    system_management_engine_service_mock import MockSystemManagementEngineService
from packages_engine.services.installer.installer_tasks.dnsmasq import DnsmasqUbuntuInstallerTask


class TestDnsmasqUbuntuInstallerTask(unittest.TestCase):
    """Dnsmasq Ubuntu Installer Task tests."""
    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: DnsmasqUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = DnsmasqUbuntuInstallerTask(
            self.notifications,
            self.engine,
            self.controller
        )

    def test_checks_for_dnsmasq_installation_status(self):
        """Checks for Dnsmasq installation status."""
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ['dnsmasq'])

    def test_notifications_flow_when_dnsmasq_installed_already(self):
        """Notifications flow when Dnsmasq installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Dnsmasq will be installed now if it is not installed.'},
                {'type': 'success',
                    'text': '\tDnsmasq is installed already. Nothing needs to be done.'},
            ]
        )

    def test_notifications_flow_when_dnsmasq_not_installed_on_success(self):
        """Notifications flow when Dnsmasq not installed on success"""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Dnsmasq will be installed now if it is not installed.'}
            ]
        )

    def test_notifications_flow_when_dnsmasq_not_installed_on_failure(self):
        """Notifications flow when Dnsmasq not installed on failure"""
        # Arrange
        operation_result = OperationResult[bool].fail('failure')
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type': 'info', 'text': 'Dnsmasq will be installed now if it is not installed.'},
                {'type': 'error', 'text': 'Command failed. Message: failure.'}
            ]
        )

    def test_no_commands_executed_when_dnsmasq_installed_already(self):
        """No commands executed when Dnsmasq installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_dnsmasq_not_installed(self):
        """Correct commands executed when Dnsmasq not installed."""
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
                    'sudo DEBIAN_FRONTEND=noninteractive apt install '
                    '-y --no-install-recommends dnsmasq',
                    'sudo systemctl disable --now dnsmasq || true',
                    'sudo systemctl reset-failed dnsmasq || true'
                ]
            ]
        )

    def test_returns_result_from_packages_controller_when_dnsmasq_not_installed_on_success(self):
        """Returns result from packages controller when Dnsmasq not installed on success"""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_result_from_packages_controller_when_dnsmasq_not_installed_on_failure(self):
        """Returns result from packages controller when Dnsmasq not installed on failure"""
        # Arrange
        operation_result = OperationResult[bool].fail('failure')
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_dnsmasq_installed(self):
        """Returns success result when Dnsmasq installed even if operation would fail."""
        # Arrange
        operation_result = OperationResult[bool].fail('failure')
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))
