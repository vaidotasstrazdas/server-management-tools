"""WireGuard VPN configuration tasks.

Configures WireGuard VPN server and interface settings.
"""

from .wireguard_ubuntu_configuration_task import WireguardUbuntuConfigurationTask
from .wireguard_windows_configuration_task import WireguardWindowsConfigurationTask

__all__ = ["WireguardUbuntuConfigurationTask", "WireguardWindowsConfigurationTask"]
