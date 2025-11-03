"""Windows nginx configuration. Nginx for Windows is not currently supported."""

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask


class NginxWindowsConfigurationTask(ConfigurationTask):
    """Nginx configuration for Windows (not implemented)."""

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Configure nginx on Windows.

        Args:
            data: Unused configuration data.

        Returns:
            Always returns failure indicating Windows is not supported.
        """
        return OperationResult[bool].fail("Not supported")
