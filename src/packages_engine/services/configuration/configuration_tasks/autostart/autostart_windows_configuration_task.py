"""Windows autostart service configuration.

Autostart service configuration for Windows is not currently supported.
"""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask


class AutostartWindowsConfigurationTask(ConfigurationTask):
    """Autostart configuration for Windows (not implemented)."""

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Configure autostart service on Windows.

        Args:
            data: Configuration data (unused).

        Returns:
            OperationResult[bool]: Always returns failure as not supported.
        """
        return OperationResult[bool].fail("Not supported")
