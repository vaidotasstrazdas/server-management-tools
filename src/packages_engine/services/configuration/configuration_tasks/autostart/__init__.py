"""Autostart service configuration tasks.

Configures system autostart services that run automatically on boot.
"""

from .autostart_ubuntu_configuration_task import AutostartUbuntuConfigurationTask
from .autostart_windows_configuration_task import AutostartWindowsConfigurationTask

__all__ = ["AutostartUbuntuConfigurationTask", "AutostartWindowsConfigurationTask"]
