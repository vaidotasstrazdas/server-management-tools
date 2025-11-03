"""Docker Gitea seeding configuration tasks.

Initializes Gitea configuration files for Docker deployments.
"""

from .docker_seed_gitea_ubuntu_configuration_task import (
    DockerSeedGiteaUbuntuConfigurationTask,
)
from .docker_seed_gitea_windows_configuration_task import (
    DockerSeedGiteaWindowsConfigurationTask,
)

__all__ = [
    "DockerSeedGiteaUbuntuConfigurationTask",
    "DockerSeedGiteaWindowsConfigurationTask",
]
