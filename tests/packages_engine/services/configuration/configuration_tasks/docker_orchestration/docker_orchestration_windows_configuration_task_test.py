import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_tasks.docker_orchestration import (
    DockerOrchestrationWindowsConfigurationTask,
)


class TestDockerOrchestrationWindowsConfigurationTask(unittest.TestCase):
    task: DockerOrchestrationWindowsConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.task = DockerOrchestrationWindowsConfigurationTask()
        self.data = ConfigurationData.default()

    def test_returns_unsupported_error(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Not supported"))
