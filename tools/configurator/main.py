"""Imports for the configurator task."""

from packages_engine.commands import ConfigureCommand
from packages_engine.services.configuration import ConfigurationDataReaderService
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderService,
)
from packages_engine.services.configuration.configuration_content_reader.content_readers import (
    RawStringContentReader,
    WireguardServerConfigContentReader,
    WireguardSharedConfigContentReader,
)
from packages_engine.services.configuration.configuration_tasks import GenericConfigurationTask
from packages_engine.services.configuration.configuration_tasks.autostart import (
    AutostartUbuntuConfigurationTask,
    AutostartWindowsConfigurationTask,
)
from packages_engine.services.configuration.configuration_tasks.dnsmasq import (
    DnsmasqUbuntuConfigurationTask,
    DnsmasqWindowsConfigurationTask,
)
from packages_engine.services.configuration.configuration_tasks.docker import (
    DockerUbuntuConfigurationTask,
    DockerWindowsConfigurationTask,
)
from packages_engine.services.configuration.configuration_tasks.nftables import (
    NftablesUbuntuConfigurationTask,
    NftablesWindowsConfigurationTask,
)
from packages_engine.services.configuration.configuration_tasks.nginx import (
    NginxUbuntuConfigurationTask,
    NginxWindowsConfigurationTask,
)
from packages_engine.services.configuration.configuration_tasks.wireguard import (
    WireguardUbuntuConfigurationTask,
    WireguardWindowsConfigurationTask,
)
from packages_engine.services.file_system import FileSystemService
from packages_engine.services.input_collection import InputCollectionService
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

    input_collection = InputCollectionService()
    config_reader = ConfigurationDataReaderService(input_collection)

    file_system = FileSystemService(system_management_service)
    wireguard_server_config_reader = WireguardServerConfigContentReader(file_system)
    wireguard_shared_config_reader = WireguardSharedConfigContentReader(file_system)
    raw_string_reader = RawStringContentReader(file_system)
    content_reader = ConfigurationContentReaderService(
        file_system,
        raw_string_reader,
        wireguard_server_config_reader,
        wireguard_shared_config_reader,
    )
    controller = PackageControllerService(system_management_service, notifications_service)

    wireguard = GenericConfigurationTask(
        WireguardUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        WireguardWindowsConfigurationTask(),
    )

    dnsmasq = GenericConfigurationTask(
        DnsmasqUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        DnsmasqWindowsConfigurationTask(),
    )

    nftables = GenericConfigurationTask(
        NftablesUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        NftablesWindowsConfigurationTask(),
    )

    docker = GenericConfigurationTask(
        DockerUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        DockerWindowsConfigurationTask(),
    )

    nginx = GenericConfigurationTask(
        NginxUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        NginxWindowsConfigurationTask(),
    )

    autostart = GenericConfigurationTask(
        AutostartUbuntuConfigurationTask(
            content_reader, file_system, notifications_service, controller
        ),
        AutostartWindowsConfigurationTask(),
    )

    command = ConfigureCommand(
        config_reader,
        [nftables],
        # config_reader, [nftables, dnsmasq, wireguard, docker, nginx, autostart]
    )
    command.execute()
