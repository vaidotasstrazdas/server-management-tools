import unittest

from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.package_controller.package_controller_service_mock import RunCommandParams
from packages_engine.commands import AutostartCommand

class TestAutostartCommand(unittest.TestCase):
    mockPackageControllerService: MockPackageControllerService
    command: AutostartCommand

    def setUp(self):
        self.mockPackageControllerService = MockPackageControllerService()
        self.command = AutostartCommand(self.mockPackageControllerService)
    
    def test_runs_correct_sequence_of_commands(self):
        # Act
        self.command.execute()

        # Assert
        params = self.mockPackageControllerService.run_command_params
        self.assertEqual(params, [
            RunCommandParams(["systemctl", "enable", "wg-quick@wg0"]),
            RunCommandParams(["systemctl", "start", "wg-quick@wg0"]),
            RunCommandParams(["ufw", "allow", "51820/udp"]),
            RunCommandParams(["systemctl", "start", "dnsmasq"]),
            RunCommandParams(["systemctl", "restart", "dnsmasq"]),
            RunCommandParams(["systemctl", "enable", "dnsmasq"]),
            RunCommandParams(["nft", "-f", "/etc/nftables.conf"]),
            RunCommandParams(["systemctl", "enable", "nftables"]),
            RunCommandParams(["docker", "compose", "up", "-d"], "/srv/stack")
        ])

    def test_ensures_correct_packages_to_be_up_and_running(self):
        # Act
        self.command.execute()

        # Assert
        params = self.mockPackageControllerService.ensure_running_params
        self.assertEqual(params, [
            'nginx'
        ])
