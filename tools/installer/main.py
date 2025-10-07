"""Necessary imports to configure the installer tool."""

from packages_engine.commands import InstallCommand
from packages_engine.services.installer import InstallerService
from packages_engine.services.installer.installer_tasks import GenericInstallerTask
from packages_engine.services.installer.installer_tasks.dnsmasq import (
    DnsmasqUbuntuInstallerTask,
    DnsmasqWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.docker import (
    DockerUbuntuInstallerTask,
    DockerWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.nftables import (
    NftablesUbuntuInstallerTask,
    NftablesWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.nginx import (
    NginxUbuntuInstallerTask,
    NginxWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.post_install_check import (
    PostInstallCheckUbuntuInstallerTask,
    PostInstallCheckWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.setup import (
    SetupUbuntuInstallerTask,
    SetupWindowsInstallerTask,
)
from packages_engine.services.installer.installer_tasks.wireguard import (
    WireguardUbuntuInstallerTask,
    WireguardWindowsInstallerTask,
)
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.package_controller import PackageControllerService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.system_management_engine_locator import (
    SystemManagementEngineLocatorService,
)


def main():
    """Entry point."""
    system_management_engine_locator_service = SystemManagementEngineLocatorService()
    engine = system_management_engine_locator_service.locate_engine()
    system_management_service = SystemManagementService(engine)

    notifications_service = NotificationsService()

    controller = PackageControllerService(system_management_service, notifications_service)
    installer_service = InstallerService()

    setup = GenericInstallerTask(
        SetupUbuntuInstallerTask(notifications_service, controller),
        SetupWindowsInstallerTask(),
    )

    wireguard = GenericInstallerTask(
        WireguardUbuntuInstallerTask(notifications_service, engine, controller),
        WireguardWindowsInstallerTask(),
    )

    dnsmasq = GenericInstallerTask(
        DnsmasqUbuntuInstallerTask(notifications_service, engine, controller),
        DnsmasqWindowsInstallerTask(),
    )

    nftables = GenericInstallerTask(
        NftablesUbuntuInstallerTask(notifications_service, engine, controller),
        NftablesWindowsInstallerTask(),
    )

    docker = GenericInstallerTask(
        DockerUbuntuInstallerTask(notifications_service, engine, controller),
        DockerWindowsInstallerTask(),
    )

    nginx = GenericInstallerTask(
        NginxUbuntuInstallerTask(notifications_service, engine, controller),
        NginxWindowsInstallerTask(),
    )

    post_install_check = GenericInstallerTask(
        PostInstallCheckUbuntuInstallerTask(notifications_service, controller),
        PostInstallCheckWindowsInstallerTask(),
    )

    command = InstallCommand(
        installer_service, [setup, wireguard, dnsmasq, nftables, docker, nginx, post_install_check]
    )
    command.execute()
