from packages_engine.services.package_controller import PackageControllerServiceContract


class AutostartCommand:
    def __init__(self, controller: PackageControllerServiceContract):
        self.controller = controller

    def execute(self):
        # WireGuard
        self.controller.run_command(["systemctl", "enable", "wg-quick@wg0"])
        self.controller.run_command(["systemctl", "start", "wg-quick@wg0"])
        self.controller.run_command(["ufw", "allow", "51820/udp"])

        # dnsmasq
        self.controller.run_command(["systemctl", "start", "dnsmasq"])
        self.controller.run_command(["systemctl", "restart", "dnsmasq"])
        self.controller.run_command(["systemctl", "enable", "dnsmasq"])

        # nftables
        self.controller.run_command(["nft", "-f", "/etc/nftables.conf"])
        self.controller.run_command(["systemctl", "enable", "nftables"])

        # docker
        self.controller.run_command(
            ["docker", "compose", "up", "-d"], "/srv/stack")

        # nginx
        self.controller.ensure_running("nginx")
