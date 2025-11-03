"""Windows configuration task for Gitea administrator setup.

This module provides a configuration task for setting up Gitea administrator users
on Windows systems. Currently, this functionality is not supported on Windows.
"""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask


class DockerSetupGiteaAdminWindowsConfigurationTask(ConfigurationTask):
    """Configuration task for setting up Gitea administrator user on Windows systems.

    This task is currently not implemented for Windows systems and will return
    a failure result when invoked.
    """

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Configure Gitea administrator user on Windows (not supported).

        Args:
            data: Configuration data (unused in current implementation).

        Returns:
            OperationResult[bool]: Always returns a failure result indicating
                the operation is not supported on Windows.
        """
        return OperationResult[bool].fail("Not supported")
