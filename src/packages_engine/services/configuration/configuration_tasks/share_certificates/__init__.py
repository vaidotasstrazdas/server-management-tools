"""Certificate sharing configuration tasks.

Shares SSL/TLS certificates with other systems or services.
"""

from .share_certificates_ubuntu_configuration_task import ShareCertificatesUbuntuConfigurationTask
from .share_certificates_windows_configuration_task import ShareCertificatesWindowsConfigurationTask

__all__ = ["ShareCertificatesUbuntuConfigurationTask", "ShareCertificatesWindowsConfigurationTask"]
