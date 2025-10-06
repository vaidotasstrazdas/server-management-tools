"""Modules necessary for the Post Install task implementation."""
from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService


class PostInstallCheckUbuntuInstallerTask(InstallerTask):
    """Runs post-install sanity checks and prints a concise status report."""

    def __init__(self, notifications: NotificationsServiceContract,
                 engine: SystemManagementEngineService,
                 controller: PackageControllerServiceContract):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info("Running post-install checks.")

        cmds = [
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

            'systemctl is-active systemd-resolved >/dev/null 2>&1 && '
            'echo "systemd-resolved is active (likely binding 127.0.0.53:53)" || '
            'echo "systemd-resolved inactive"',

            # Docker non-root check (for the default Multipass user)
            'echo; echo "--- Docker group ---"',

            'id -nG ubuntu | tr " " "\\n" | grep -qx docker && '
            'echo "user ubuntu in docker group: YES" || '
            'echo "user ubuntu in docker group: NO"',

            'test -S /var/run/docker.sock && ls -l /var/run/docker.sock || true',

            # Is UFW active? (we'll want it OFF when nftables is the owner)
            'sudo ufw status || true',

            # Who owns /var/run/docker.sock and is 'ubuntu' in docker group?
            'id -nG ubuntu | tr \' \' \'\n\' | grep -qx docker && '
            'echo "ubuntu in docker group: YES" || echo "ubuntu in docker group: NO"'
        ]

        result = self.controller.run_raw_commands(cmds)

        # We *expect* some "inactive/disabled" states in install-only mode,
        # so treat this as a best-effort info report.
        if not result.success:
            self.notifications.error(
                "Some checks failed to run (shell error). See output above."
            )
            return result

        self.notifications.success("Post-install checks completed.")
        return OperationResult[bool].succeed(True)
