import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData

from packages_engine.services.configuration.configuration_tasks.autostart import AutostartWindowsConfigurationTask

class TestAutostartWindowsConfigurationTask(unittest.TestCase):
    task: AutostartWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = AutostartWindowsConfigurationTask()
        self.data = ConfigurationData.default()
    
    def test_returns_unsupported_error(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail('Not supported'))