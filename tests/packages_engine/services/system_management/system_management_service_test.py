"""Tests for SystemManagementService - verifies delegation to platform-specific engine."""

import unittest

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.system_management import SystemManagementService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import (
    ExecuteCommandParams,
    MockSystemManagementEngineService,
)


class TestSystemManagementService(unittest.TestCase):
    """
    Test suite for SystemManagementService.

    Verifies that SystemManagementService correctly delegates all operations
    to the underlying platform-specific engine service.
    """

    system_management_engine_service: MockSystemManagementEngineService
    service: SystemManagementService

    def setUp(self):
        self.system_management_engine_service = MockSystemManagementEngineService()
        self.service = SystemManagementService(self.system_management_engine_service)

    def test_is_installed_calls_check_from_engine(self):
        """Is instaled calls check from engine."""
        # Act
        self.service.is_installed("package")

        # Assert
        params = self.system_management_engine_service.is_installed_params
        self.assertEqual(params, ["package"])

    def test_is_installed_result_is_returned_from_engine_case_1(self):
        """Is installed result is returned from engine (case 1)"""
        # Arrange
        self.system_management_engine_service.is_installed_result = True

        # Act
        result = self.service.is_installed("package")

        # Assert
        self.assertTrue(result)

    def test_is_installed_result_is_returned_from_engine_case_2(self):
        """Is installed result is returned from engine (case 2)"""
        # Arrange
        self.system_management_engine_service.is_installed_result = False

        # Act
        result = self.service.is_installed("package")

        # Assert
        self.assertFalse(result)

    def test_install_calls_engine(self):
        """Install calls engine."""
        # Act
        self.service.install("package")

        # Assert
        params = self.system_management_engine_service.install_params
        self.assertEqual(params, ["package"])

    def test_install_returns_engine_result(self):
        """Install returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.install_result = dto

        # Act
        result = self.service.install("package")

        # Assert
        self.assertEqual(result, dto)

    def test_is_running_calls_engine(self):
        """Is running cals engine."""
        # Act
        self.service.is_running("package")

        # Assert
        params = self.system_management_engine_service.is_running_params
        self.assertEqual(params, ["package"])

    def test_is_running_returns_engine_result(self):
        """Is running returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.is_running_result = dto

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(result, dto)

    def test_start_calls_engine(self):
        """Start calls engine."""
        # Act
        self.service.start("package")

        # Assert
        params = self.system_management_engine_service.start_params
        self.assertEqual(params, ["package"])

    def test_start_returns_engine_result(self):
        """Start returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.start_result = dto

        # Act
        result = self.service.start("package")

        # Assert
        self.assertEqual(result, dto)

    def test_restart_calls_engine(self):
        """Restart calls engine."""
        # Act
        self.service.restart("package")

        # Assert
        params = self.system_management_engine_service.restart_params
        self.assertEqual(params, ["package"])

    def test_restart_returns_engine_result(self):
        """Restart returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.restart_result = dto

        # Act
        result = self.service.restart("package")

        # Assert
        self.assertEqual(result, dto)

    def test_execute_command_calls_engine(self):
        """Execute commands calls engine."""
        # Act
        self.service.execute_command(["foo", "bar"], "/src")

        # Assert
        params = self.system_management_engine_service.execute_command_params
        self.assertEqual(params, [ExecuteCommandParams(["foo", "bar"], "/src")])

    def test_execute_command_returns_engine_result(self):
        """Execute command returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.execute_command_result = dto

        # Act
        result = self.service.execute_command(["foo", "bar"], "/src")

        # Assert
        self.assertEqual(result, dto)

    def test_execute_raw_command_calls_engine(self):
        """Execute raw command calls engine."""
        # Act
        self.service.execute_raw_command("foo bar")

        # Assert
        params = self.system_management_engine_service.execute_raw_command_params
        self.assertEqual(params, ["foo bar"])

    def test_execute_raw_command_returns_engine_result(self):
        """Execute raw command returns engine result."""
        # Arrange
        dto = OperationResult[bool].fail("Install not success", 9)
        self.system_management_engine_service.execute_raw_command_result = dto

        # Act
        result = self.service.execute_raw_command("foo bar")

        # Assert
        self.assertEqual(result, dto)
