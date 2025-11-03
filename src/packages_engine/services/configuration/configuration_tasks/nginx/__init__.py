"""Nginx web server configuration tasks.

Configures Nginx reverse proxy and web server settings.
"""

from .nginx_ubuntu_configuration_task import NginxUbuntuConfigurationTask
from .nginx_windows_configuration_task import NginxWindowsConfigurationTask

__all__ = ["NginxUbuntuConfigurationTask", "NginxWindowsConfigurationTask"]
