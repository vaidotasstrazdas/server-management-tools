"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.docker import DockerUbuntuInstallerTask
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)
from packages_engine.services.system_management_engine.system_management_engine_service_mock import (
    MockSystemManagementEngineService,
)


class TestDockerUbuntuInstallerTask(unittest.TestCase):
    """Docker Ubuntu Installer Task Tests"""

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
        """Checks for Docker installation status"""
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ["docker-ce"])

    def test_notifications_flow_when_docker_installed_already(self):
        """Notifications flow when Docker installed already."""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "Docker will be installed now if it is not installed."},
                {
                    "type": "success",
                    "text": "\tDocker is installed already. Nothing needs to be done.",
                },
            ],
        )

    def test_notifications_flow_when_docker_not_installed_on_success(self):
        """Notifications flow when Docker not installed on success"""
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
            [{"type": "info", "text": "Docker will be installed now if it is not installed."}],
        )

    def test_notifications_flow_when_docker_not_installed_on_failure(self):
        """Notifications flow when Docker not installed on success"""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {"type": "info", "text": "Docker will be installed now if it is not installed."},
                {"type": "error", "text": "Command failed. Message: failure."},
            ],
        )

    def test_no_commands_executed_when_docker_installed_already(self):
        """No commands executed when Docker installed already"""
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_docker_not_installed(self):
        """Correct commands executed when Docker not installed."""
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
                    # 0) Remove conflicting packages (safe to run even if none present)
                    "for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker "
                    "containerd runc; do sudo apt-get -y remove $pkg >/dev/null 2>&1 || true; done",
                    # 1) Keyring dir + official key (per docs)
                    "sudo install -m 0755 -d /etc/apt/keyrings",
                    "test -f /etc/apt/keyrings/docker.asc || sudo curl -fsSL "
                    "https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
                    "sudo chmod a+r /etc/apt/keyrings/docker.asc",
                    # 2) Repo line (idempotent write)
                    "grep -qs '^deb .*download.docker.com/linux/ubuntu' "
                    "/etc/apt/sources.list.d/docker.list || "
                    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] '
                    "https://download.docker.com/linux/ubuntu "
                    '$(. /etc/os-release && echo \\"${UBUNTU_CODENAME:-$VERSION_CODENAME}\\") stable" | '
                    "sudo tee /etc/apt/sources.list.d/docker.list >/dev/null",
                    # 3) Update indexes NOW that the repo exists
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get update",
                    # 4) Install Docker Engine + friends (no recommends keeps it lean)
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "
                    "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                ]
            ],
        )

    def test_returns_result_from_packages_controller_when_docker_not_installed_on_success(self):
        """returns result from packages controller when Docker not installed on success"""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_result_from_packages_controller_when_docker_not_installed_on_failure(self):
        """returns result from packages controller when Docker not installed on failure"""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_docker_installed(self):
        """Returns success result when Docker installed even if command would fail."""
        # Arrange
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = OperationResult[bool].fail("failure")

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))
