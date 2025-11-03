"""Generic platform-agnostic configuration task dispatcher.

Routes configuration requests to platform-specific implementations based on the OS.
"""

import sys

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

from .configuration_task import ConfigurationTask


class GenericConfigurationTask(ConfigurationTask):
    """Platform-agnostic configuration task that delegates to OS-specific implementations."""

    def __init__(self, ubuntu: ConfigurationTask, windows: ConfigurationTask):
        """Initialize with platform-specific configuration tasks.

        Args:
            ubuntu: Configuration task for Linux/Ubuntu systems.
            windows: Configuration task for Windows systems.
        """
        self.ubuntu = ubuntu
        self.windows = windows

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Route configuration to the appropriate platform implementation.

        Args:
            data: Configuration data to apply.

        Returns:
            OperationResult[bool]: Result from the platform-specific implementation.
        """
        if sys.platform.startswith("win"):
            return self.windows.configure(data)
        elif sys.platform.startswith("linux"):
            return self.ubuntu.configure(data)

        return OperationResult[bool].fail(f'Not supported platform "{sys.platform}"')
