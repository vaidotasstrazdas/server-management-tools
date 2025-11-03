"""Dnsmasq DNS/DHCP server configuration tasks.

Configures dnsmasq for DNS and DHCP services.
"""

from .dnsmasq_ubuntu_configuration_task import DnsmasqUbuntuConfigurationTask
from .dnsmasq_windows_configuration_task import DnsmasqWindowsConfigurationTask

__all__ = ["DnsmasqUbuntuConfigurationTask", "DnsmasqWindowsConfigurationTask"]
