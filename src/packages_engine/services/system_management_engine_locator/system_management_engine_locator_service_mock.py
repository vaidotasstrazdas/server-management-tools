"""Mock System Management Engine Locator Service - test double for engine location."""

from packages_engine.services.system_management_engine.system_management_engine_service import (
    SystemManagementEngineService,
)

from .system_management_engine_locator_service_contract import (
    SystemManagementEngineLocatorServiceContract,
)


class MockSystemManagementEngineLocatorService(SystemManagementEngineLocatorServiceContract):
    """
    Mock implementation of SystemManagementEngineLocatorService for testing purposes.

    Tracks the number of times locate_engine is called and returns a configured
    engine service instance, allowing tests to verify engine location behavior
    and control which engine is returned.

    Attributes:
        locate_engine_triggered_times: Counter for number of locate_engine calls.
        locate_engine_result: The engine service instance to return from locate_engine.
    """

    locate_engine_triggered_times = 0
    locate_engine_result: SystemManagementEngineService

    def locate_engine(self) -> SystemManagementEngineService:
        """
        Record a locate_engine call and return configured engine.

        Increments the trigger counter and returns the configured engine service.

        Returns:
            The configured locate_engine_result instance.
        """
        self.locate_engine_triggered_times = self.locate_engine_triggered_times + 1
        return self.locate_engine_result
