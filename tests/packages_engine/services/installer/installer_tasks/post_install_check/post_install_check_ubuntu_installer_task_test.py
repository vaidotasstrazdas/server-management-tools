"""Necessary imports for the tests."""

import unittest

from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks.post_install_check import (
    PostInstallCheckUbuntuInstallerTask,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestPostInstallCheckUbuntuInstallerTask(unittest.TestCase):
    """PostInstallCheck Ubuntu Installer Task Tests"""

    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: PostInstallCheckUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = PostInstallCheckUbuntuInstallerTask(self.notifications, self.controller)

    def test_notifications_flow_on_success(self):
        """Notifications flow on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {
                    "type": "info",
                    "text": "Running post-install checks.",
                },
                {
                    "type": "success",
                    "text": "Post-install checks completed.",
                },
            ],
        )

    def test_notifications_flow_on_failure(self):
        """Notifications flow on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.controller.run_raw_commands_result = operation_result

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {
                    "type": "info",
                    "text": "Running post-install checks.",
                },
                {
                    "type": "error",
                    "text": "Some checks failed to run (shell error). See output above.",
                },
            ],
        )

    def test_correct_commands_executed(self):
        """Correct commands executed."""
        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(
            params,
            [
                [
                    # Packages present?
                    'echo "--- Packages ---"',
                    'dpkg -s wireguard >/dev/null 2>&1 && echo "wireguard: OK" '
                    '|| echo "wireguard: MISSING"',
                    'dpkg -s wireguard-tools >/dev/null 2>&1 && echo "wireguard-tools: OK" '
                    '|| echo "wireguard-tools: MISSING"',
                    'dpkg -s dnsmasq >/dev/null 2>&1 && echo "dnsmasq: OK" || echo "dnsmasq: MISSING"',
                    'dpkg -s nftables >/dev/null 2>&1 && echo "nftables: OK" || echo "nftables: MISSING"',
                    'dpkg -s nginx >/dev/null 2>&1 && echo "nginx: OK" || echo "nginx: MISSING"',
                    'dpkg -s docker-ce >/dev/null 2>&1 && echo "docker-ce: OK" '
                    '|| echo "docker-ce: MISSING"',
                    # Services expected states for install-only
                    'echo; echo "--- Services (enabled/active) ---"',
                    'printf "wg-quick@wg0:   %s / %s\n" "$(systemctl is-enabled wg-quick@wg0 '
                    '2>/dev/null||echo n/a)" "$(systemctl is-active wg-quick@wg0 2>/dev/null||echo n/a)"',
                    'printf "dnsmasq:       %s / %s\n" "$(systemctl is-enabled dnsmasq '
                    '2>/dev/null||echo n/a)" "$(systemctl is-active dnsmasq 2>/dev/null||echo n/a)"',
                    'printf "nftables:      %s / %s\n" "$(systemctl is-enabled nftables '
                    '2>/dev/null||echo n/a)" "$(systemctl is-active nftables 2>/dev/null||echo n/a)"',
                    'printf "nginx:         %s / %s\n" "$(systemctl is-enabled nginx '
                    '2>/dev/null||echo n/a)" "$(systemctl is-active nginx 2>/dev/null||echo n/a)"',
                    'printf "docker:        %s / %s\n" "$(systemctl is-enabled docker '
                    '2>/dev/null||echo n/a)" "$(systemctl is-active docker 2>/dev/null||echo n/a)"',
                    # Port ownership highlights
                    'echo; echo "--- Ports 53/80/443/51820 ---"',
                    'ss -lntup | grep -E ":(53|80|443|51820)\\b" || echo "No listeners on 53/80/443/51820"',
                    # Who owns :53 (helps explain dnsmasq failure)
                    'echo; echo "--- Resolver ---"',
                    "systemctl is-active systemd-resolved >/dev/null 2>&1 && "
                    'echo "systemd-resolved is active (likely binding 127.0.0.53:53)" || '
                    'echo "systemd-resolved inactive"',
                    # Docker non-root check (for the default Multipass user)
                    'echo; echo "--- Docker group ---"',
                    'id -nG ubuntu | tr " " "\\n" | grep -qx docker && '
                    'echo "user ubuntu in docker group: YES" || '
                    'echo "user ubuntu in docker group: NO"',
                    "test -S /var/run/docker.sock && ls -l /var/run/docker.sock || true",
                    # Is UFW active? (we'll want it OFF when nftables is the owner)
                    "sudo ufw status || true",
                    # Who owns /var/run/docker.sock and is 'ubuntu' in docker group?
                    "id -nG ubuntu | tr ' ' '\n' | grep -qx docker && "
                    'echo "ubuntu in docker group: YES" || echo "ubuntu in docker group: NO"',
                ]
            ],
        )

    def test_returns_result_from_packages_controller_on_success(self):
        """Returns result from packages controller on success."""
        # Arrange
        operation_result = OperationResult[bool].succeed(True)
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_result_from_packages_controller_on_failure(self):
        """Returns result from packages controller on failure."""
        # Arrange
        operation_result = OperationResult[bool].fail("failure")
        self.controller.run_raw_commands_result = operation_result

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)
