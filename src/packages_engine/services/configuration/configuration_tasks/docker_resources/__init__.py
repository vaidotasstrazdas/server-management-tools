"""Docker resources configuration tasks.

Manages Docker directories, docker-compose files, and permissions.
"""

from .docker_resources_ubuntu_configuration_task import (
    DockerResourcesUbuntuConfigurationTask,
)
from .docker_resources_windows_configuration_task import (
    DockerResourcesWindowsConfigurationTask,
)

__all__ = [
    "DockerResourcesUbuntuConfigurationTask",
    "DockerResourcesWindowsConfigurationTask",
]
