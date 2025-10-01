import unittest

from packages_engine.models import OperationResult

from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import MockSystemManagementEngineService
from packages_engine.services.installer.installer_tasks.docker import DockerUbuntuInstallerTask

class TestDockerUbuntuInstallerTask(unittest.TestCase):
    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: DockerUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = DockerUbuntuInstallerTask(self.notifications, self.engine, self.controller)
    
    def test_checks_for_docker_installation_status(self):
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ['docker-ce'])

    def test_notification_flow_when_docker_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Docker will be installed now if it is not installed.'},
                {'type':'success','text':'\tDocker is installed already. Nothing needs to be done.'},
            ]
        )

    def test_notification_flow_when_docker_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Docker will be installed now if it is not installed.'}
            ]
        )

    def test_no_commands_executed_when_docker_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_docker_not_installed(self):
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
                    'sudo apt install -y ca-certificates curl gnupg',
                    'sudo install -m 0755 -d /etc/apt/keyrings',
                    'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null',
                    'sudo apt update',
                    'sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin',
                    'sudo systemctl enable --now docker',
                ]
            ]
        )

    def test_returns_result_from_packages_controller_when_docker_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = OperationResult[bool].succeed(True)

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_docker_installed(self):
        # Arrange
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = OperationResult[bool].fail('failure')

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))