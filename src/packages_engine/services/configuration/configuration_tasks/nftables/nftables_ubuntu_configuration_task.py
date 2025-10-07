"""Necessary imports."""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class NftablesUbuntuConfigurationTask(ConfigurationTask):
    """Nftables Ubuntu Configuration Task Implementation."""

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info("Reading Nftables Config template data.")

        # Read your rendered rules for the *host* table (from your template path)
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/nftables.d/10-host-fw.nft",
        )
        if not read_result.success or read_result.data is None:
            self.notifications.error("\tReading host-fw rules failed.")
            return read_result.as_fail()
        self.notifications.success("\tHost-fw rules read successfully.")

        # Ensure directory and write files
        self.notifications.info("Writing nftables configuration files.")
        mkdir_res = self.controller.run_raw_commands(["sudo install -d -m 0755 /etc/nftables.d"])
        if not mkdir_res.success:
            self.notifications.error("\tCreating /etc/nftables.d failed.")
            return mkdir_res.as_fail()

        # Write main /etc/nftables.conf (tiny include-only file)
        main_conf = '#!/usr/sbin/nft -f\ninclude "/etc/nftables.d/*.nft"\n'
        write_main = self.file_system.write_text("/etc/nftables.conf", main_conf)
        if not write_main.success:
            self.notifications.error("\tWriting /etc/nftables.conf failed.")
            return write_main.as_fail()

        # Write your host rules
        write_host = self.file_system.write_text("/etc/nftables.d/10-host-fw.nft", read_result.data)
        if not write_host.success:
            self.notifications.error("\tWriting /etc/nftables.d/10-host-fw.nft failed.")
            return write_host.as_fail()
        self.notifications.success("\tNftables files written.")

        # Apply system settings (forwarding/bridge visibility) — optional but useful
        self.notifications.info("Applying sysctl/module settings.")
        sysctl_res = self.controller.run_raw_commands(
            [
                'echo "br_netfilter" | sudo tee /etc/modules-load.d/br_netfilter.conf >/dev/null',
                'echo "net.bridge.bridge-nf-call-iptables = 1" | sudo tee /etc/sysctl.d/99-bridge-nf.conf >/dev/null',
                'echo "net.ipv4.ip_forward = 1"               | sudo tee /etc/sysctl.d/99-ipforward.conf   >/dev/null',
                "sudo modprobe br_netfilter || true",
                "sudo sysctl --system",
            ]
        )
        if not sysctl_res.success:
            self.notifications.error("\tApplying sysctl/module settings failed.")
            return sysctl_res.as_fail()
        self.notifications.success("\tApplying sysctl/module settings succeeded.")

        # Make sure iptables defaults to the nft backend (harmless if already set)
        self.notifications.info("Setting iptables alternatives.")
        alt_res = self.controller.run_raw_commands(
            [
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends iptables nftables",
                "sudo update-alternatives --set iptables   /usr/sbin/iptables-nft",
                "sudo update-alternatives --set ip6tables  /usr/sbin/ip6tables-nft",
                "sudo update-alternatives --set arptables  /usr/sbin/arptables-nft",
                "sudo update-alternatives --set ebtables   /usr/sbin/ebtables-nft",
            ]
        )
        if not alt_res.success:
            self.notifications.error("\tSetting iptables alternatives failed.")
            return alt_res.as_fail()
        self.notifications.success("\tSetting iptables alternatives succeeded.")

        # Validate then load ONLY your table (don’t restart the service yet)
        self.notifications.info("\tLoading nft rules.")
        apply_res = self.controller.run_raw_commands(
            [
                # If table exists, delete it to avoid “File exists” on reload
                'sudo nft list tables | grep -q "table inet host_fw" && sudo nft delete table inet host_fw || true',
                "sudo nft -c -f /etc/nftables.d/10-host-fw.nft",
                "sudo nft -f /etc/nftables.d/10-host-fw.nft",
                # Enable persistence on reboot (service will load /etc/nftables.conf which includes *.nft)
                "sudo systemctl enable nftables",
                # Do NOT restart nftables here: it would try to load /etc/nftables.conf again
                # and might error if it re-runs 'add table' while live. We already applied above.
            ]
        )
        if not apply_res.success:
            self.notifications.error("\tLoading nft rules failed.")
            return apply_res.as_fail()
        self.notifications.success("\tLoading nft rules succeeded.")

        self.notifications.success("\tNftables configured successfully (Docker-safe).")
        return OperationResult[bool].succeed(True)
