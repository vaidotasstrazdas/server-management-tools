"""Tests for SystemManagementEngineLocatorService - verifies platform engine location."""

import unittest

from packages_engine.services.system_management_engine.engines.linux_ubuntu_engine_service import (
    LinuxUbuntuEngineService,
)
from packages_engine.services.system_management_engine_locator.system_management_engine_locator_service import (
    SystemManagementEngineLocatorService,
)


class TestSystemManagementEngineLocatorService(unittest.TestCase):
    """
    Test suite for SystemManagementEngineLocatorService.

    Verifies that the locator service returns the correct platform-specific
    engine implementation.
    """

    service: SystemManagementEngineLocatorService

    def setUp(self):
        self.service = SystemManagementEngineLocatorService()

    def test_returns_linux_engine(self):
        """returns Linux Ubuntu engine"""
        # Act
        result = self.service.locate_engine()

        # Assert
        self.assertIsInstance(result, LinuxUbuntuEngineService)
