"""WireGuard configuration sharing tasks.

Shares WireGuard configuration files with peers.
"""

from .wireguard_share_ubuntu_configuration_task import WireguardShareUbuntuConfigurationTask
from .wireguard_share_windows_configuration_task import WireguardShareWindowsConfigurationTask

__all__ = ["WireguardShareUbuntuConfigurationTask", "WireguardShareWindowsConfigurationTask"]
