import unittest

from packages_engine.services.system_management_engine_locator.system_management_engine_locator_service import SystemManagementEngineLocatorService
from packages_engine.services.system_management_engine.engines.linux_ubuntu_engine_service import LinuxUbuntuEngineService

package_name = 'packages_engine.services.system_management_engine.engines.linux_ubuntu_engine_service'

class TestSystemManagementEngineLocatorService(unittest.TestCase):
    service: SystemManagementEngineLocatorService

    def setUp(self):
        self.service = SystemManagementEngineLocatorService()
    
    def test_returns_linux_engine(self):
        # Act
        result = self.service.locate_engine()

        # Assert
        self.assertIsInstance(result, LinuxUbuntuEngineService)