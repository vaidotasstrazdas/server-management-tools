"""Docker Gitea administrator setup configuration tasks.

This module provides configuration tasks for setting up Gitea administrator users
on different operating systems using Docker containers.
"""

from .docker_setup_gitea_admin_ubuntu_configuration_task import (
    DockerSetupGiteaAdminUbuntuConfigurationTask,
)
from .docker_setup_gitea_admin_windows_configuration_task import (
    DockerSetupGiteaAdminWindowsConfigurationTask,
)

__all__ = [
    "DockerSetupGiteaAdminUbuntuConfigurationTask",
    "DockerSetupGiteaAdminWindowsConfigurationTask",
]
