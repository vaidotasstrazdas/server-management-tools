from packages_engine.services.installer import InstallerService
from packages_engine.services.installer.installer_tasks import GenericInstallerTask
from packages_engine.services.installer.installer_tasks.dnsmasq import DnsmasqUbuntuInstallerTask
from packages_engine.services.installer.installer_tasks.dnsmasq import DnsmasqWindowsInstallerTask
from packages_engine.services.installer.installer_tasks.docker import DockerUbuntuInstallerTask
from packages_engine.services.installer.installer_tasks.docker import DockerWindowsInstallerTask
from packages_engine.services.installer.installer_tasks.nginx import NginxUbuntuInstallerTask
from packages_engine.services.installer.installer_tasks.nginx import NginxWindowsInstallerTask
from packages_engine.services.installer.installer_tasks.nftables import NftablesUbuntuInstallerTask
from packages_engine.services.installer.installer_tasks.nftables import NftablesWindowsInstallerTask
from packages_engine.services.installer.installer_tasks.wireguard import WireguardUbuntuInstallerTask
from packages_engine.services.installer.installer_tasks.wireguard import WireguardWindowsInstallerTask
from packages_engine.services.package_controller import PackageControllerService
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.notifications import NotificationsService
from packages_engine.services.system_management_engine_locator import SystemManagementEngineLocatorService

def main():
    systemManagementEngineLocatorService = SystemManagementEngineLocatorService()
    engine = systemManagementEngineLocatorService.locate_engine()
    systemManagementService = SystemManagementService(engine)

    notificationsService = NotificationsService()

    controller = PackageControllerService(systemManagementService, notificationsService)
    installerService = InstallerService()

    wireguard = GenericInstallerTask(
        WireguardUbuntuInstallerTask(notificationsService, engine, controller),
        WireguardWindowsInstallerTask()
    )

    dnsmasq = GenericInstallerTask(
        DnsmasqUbuntuInstallerTask(notificationsService, engine, controller),
        DnsmasqWindowsInstallerTask()
    )

    nftables = GenericInstallerTask(
        NftablesUbuntuInstallerTask(notificationsService, engine, controller),
        NftablesWindowsInstallerTask()
    )

    docker = GenericInstallerTask(
        DockerUbuntuInstallerTask(notificationsService, engine, controller),
        DockerWindowsInstallerTask()
    )

    nginx = GenericInstallerTask(
        NginxUbuntuInstallerTask(notificationsService, engine, controller),
        NginxWindowsInstallerTask()
    )
    
    installerService.install([wireguard, dnsmasq, nftables, docker, nginx])