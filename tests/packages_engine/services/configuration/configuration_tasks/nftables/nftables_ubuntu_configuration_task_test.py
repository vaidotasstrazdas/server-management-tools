import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import MockConfigurationContentReaderService
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService
from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.configuration.configuration_tasks.nftables import NftablesUbuntuConfigurationTask

class TestNftablesUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: NftablesUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = NftablesUbuntuConfigurationTask(self.reader, self.file_system, self.notifications, self.controller)
        self.data = ConfigurationData.default()
    
    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))