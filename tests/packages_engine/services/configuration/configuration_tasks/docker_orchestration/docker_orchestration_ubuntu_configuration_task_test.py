"""Tests for DockerOrchestrationUbuntuConfigurationTask. Validates Docker network, DNS, and compose orchestration on Ubuntu."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_tasks.docker_orchestration import (
    DockerOrchestrationUbuntuConfigurationTask,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestDockerOrchestrationUbuntuConfigurationTask(unittest.TestCase):
    """Test suite for DockerOrchestrationUbuntuConfigurationTask. Verifies network setup, DNS config, and container orchestration."""

    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: DockerOrchestrationUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = DockerOrchestrationUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.domain_name = "internal.app"
        self.maxDiff = None

    def test_happy_path(self):
        """Verifies successful configuration returns success result."""
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_notifications_flow(self):
        """Verifies correct notification messages are sent during successful orchestration."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Orchestrating Docker containers.", "type": "info"},
                {"text": "\tOrchestrating Docker containers succeeded.", "type": "success"},
            ],
        )

    def test_runs_commands(self):
        """Verifies all required Docker network, DNS, and compose commands are executed."""
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    # network (only create if missing)
                    "sudo docker network inspect vpn-internal >/dev/null 2>&1 || "
                    "sudo docker network create --driver bridge --attachable vpn-internal",
                    # daemon.json must exist first
                    "sudo install -d -m 0755 /etc/docker",
                    "test -f /etc/docker/daemon.json || echo '{}' | sudo tee /etc/docker/daemon.json >/dev/null",
                    # merge DNS & search domain (idempotent & deduped)
                    f"sudo jq --arg dns '10.10.0.1' --arg search '{self.data.domain_name}' "
                    '\'.dns = ((.dns // []) + [$dns] | unique) | ."dns-search" = ((."dns-search" // []) + [$search] | unique)\' '
                    "/etc/docker/daemon.json | sudo tee /etc/docker/daemon.json.tmp >/dev/null && "
                    "sudo mv /etc/docker/daemon.json.tmp /etc/docker/daemon.json && "
                    "sudo chown root:root /etc/docker/daemon.json && sudo chmod 0644 /etc/docker/daemon.json",
                    # optionally ensure docker starts after wg0 so 10.10.0.1 DNS is up on boot
                    "sudo install -d -m 0755 /etc/systemd/system/docker.service.d",
                    "sudo bash -lc 'cat > /etc/systemd/system/docker.service.d/10-after-wg0.conf <<EOF\n[Unit]\nAfter=wg-quick@wg0.service\nWants=wg-quick@wg0.service\nEOF'",
                    "sudo systemctl daemon-reload",
                    "sudo systemctl enable docker",
                    "sudo systemctl restart docker",
                    # compose: pull updated images and up with --remove-orphans
                    "cd /srv/stack && sudo docker compose pull --quiet || true",
                    "cd /srv/stack && sudo docker compose config -q",
                    "cd /srv/stack && sudo docker compose up -d --remove-orphans",
                    # wait for healthchecks so subsequent tasks can rely on services being ready
                    "cd /srv/stack && sudo docker compose ps",
                    "timeout 120 bash -lc '"
                    '  echo "Waiting for Postgres health=healthy…";'
                    "  until [[ $(docker inspect -f {{.State.Health.Status}} postgres 2>/dev/null || echo none) == healthy ]]; do sleep 2; done;"
                    '  echo "Postgres is healthy. Probing Gitea on 127.0.0.1:3000…";'
                    "  for i in {1..60}; do "
                    '    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/ || true); '
                    '    if [[ $code =~ ^(200|30[12])$ ]]; then echo "Gitea is responding ($code)."; exit 0; fi; '
                    "    sleep 2; "
                    "  done; "
                    '  echo "Gitea did not respond with 200/301/302 within timeout; continuing anyway.";'
                    "' || true",
                    # show ports bound to loopback (host side)
                    "ss -lntup | grep -E '(:5432|:3000|:2222|:8081)\\b' || true",
                    # DNS smoke test from a throwaway container via Docker’s embedded DNS
                    f"sudo docker run --rm --network vpn-internal busybox sh -lc "
                    f"'nslookup gitea.{self.data.domain_name} 127.0.0.11 && nslookup postgresql.{self.data.domain_name} 127.0.0.11' || true",
                ]
            ],
        )

    def test_failure_to_run_commands_results_in_failure(self):
        """Verifies command execution failure propagates as failed result."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_run_commands_results_in_failure_notifications_flow(self):
        """Verifies error notifications are sent when command execution fails."""
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Orchestrating Docker containers.", "type": "info"},
                {"text": "\tFailed to orchestrate Docker containers.", "type": "error"},
            ],
        )
