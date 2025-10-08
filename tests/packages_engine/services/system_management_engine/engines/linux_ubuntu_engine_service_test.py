"""Tests for LinuxUbuntuEngineService - verifies Ubuntu-specific system operations."""

import subprocess
import sys
import unittest
from unittest.mock import MagicMock, call, patch

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.system_management_engine.engines.linux_ubuntu_engine_service import (
    LinuxUbuntuEngineService,
)

PACKAGE_NAME = (
    "packages_engine.services.system_management_engine.engines.linux_ubuntu_engine_service"
)


class TestLinuxUbuntuEngineServiceData:
    """
    Helper class providing test data and expected call patterns.

    Contains methods that return expected subprocess.run call patterns
    for various system operations.
    """

    def update_call(self):
        """Return expected call pattern for apt-get update."""
        return call(["sudo", "apt-get", "update"], stdout=sys.stdout, stderr=sys.stderr, check=True)

    def install_call(self):
        """Return expected call pattern for apt-get install."""
        return call(
            ["sudo", "apt-get", "install", "-y", "package"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=True,
        )

    def raw_command_call(self, command: str):
        """
        Return expected call pattern for raw bash command.

        Args:
            command: The command string to execute.

        Returns:
            Expected call pattern for bash -lc execution.
        """
        return call(["bash", "-lc", command], stdout=sys.stdout, stderr=sys.stderr, check=True)


class TestLinuxUbuntuEngineService(unittest.TestCase):
    """
    Test suite for LinuxUbuntuEngineService.

    Verifies that LinuxUbuntuEngineService correctly executes Ubuntu-specific
    system operations using subprocess with proper arguments and error handling.
    """

    service: LinuxUbuntuEngineService
    data: TestLinuxUbuntuEngineServiceData

    def setUp(self):
        self.service = LinuxUbuntuEngineService()
        self.data = TestLinuxUbuntuEngineServiceData()

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_correct_calls_are_made_to_check_package_installation_status(self, mock_run: MagicMock):
        """correct calls are made to check package installation status."""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.is_installed("package")

        # Assert
        mock_run.assert_called_once_with(
            ["dpkg", "-s", "package"], stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_installed_returns_true_on_successful_check(self, mock_run: MagicMock):
        """is installed returns true on successful check"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.is_installed("package")

        # Assert
        self.assertTrue(result)

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_installed_returns_false_on_failed_check(self, mock_run: MagicMock):
        """is installed returns false on failed check"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=1, cmd=""),
        ]

        # Act
        result = self.service.is_installed("package")

        # Assert
        self.assertFalse(result)

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_update_call_is_made_to_install_package(self, mock_run: MagicMock):
        """update call is made to install package."""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.install("package")

        # Assert
        mock_run.assert_has_calls(
            calls=[
                self.data.update_call(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_install_call_is_made_to_install_package(self, mock_run: MagicMock):
        """install call is made to install package"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.install("package")

        # Assert
        mock_run.assert_has_calls(calls=[self.data.install_call()], any_order=False)

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_install_calls_are_made_in_correct_order(self, mock_run: MagicMock):
        """install calls are made in correct order"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.install("package")

        # Assert
        mock_run.assert_has_calls(
            calls=[
                self.data.update_call(),
                self.data.install_call(),
            ],
            any_order=False,
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_install_results_in_success_when_process_completes_successfully(
        self, mock_run: MagicMock
    ):
        """install results in success when process complete successfully"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.install("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_install_results_in_failure_when_update_check_fails(self, mock_run: MagicMock):
        """install results in falure when update check fails."""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=1, cmd=""),
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.install("package")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Failed to install 'package'. Code: 1.", 1)
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_install_results_in_failure_when_install_call_fails(self, mock_run: MagicMock):
        """install results in failure when install call fails"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.install("package")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Failed to install 'package'. Code: 123.", 123)
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_uses_correct_calls_to_check_running_status(self, mock_run: MagicMock):
        """is running uses correct calls to check running status"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="active"),
        ]

        # Act
        self.service.is_running("package")

        # Assert
        mock_run.assert_called_once_with(
            ["systemctl", "is-active", "package"], capture_output=True, text=True, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_success_of_true_on_active_result(self, mock_run: MagicMock):
        """is running returns success of true on active result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="active"),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_success_of_false_on_inactive_result(self, mock_run: MagicMock):
        """is running returns success of false on inactive result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="inactive"),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(False))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_success_of_false_on_failed_result(self, mock_run: MagicMock):
        """is running returns success of false on failed result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="failed"),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(False))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_failure_on_unknown_result(self, mock_run: MagicMock):
        """is running returns failure on unknown result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="unknown"),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(
            result,
            OperationResult[bool].fail(
                "Failed to check running status for the 'package' due to unknown result returned. Result: 'unknown'",
                0,
            ),
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_failure_on_subprocess_failure(self, mock_run: MagicMock):
        """is running returns failure on subprocess failure"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(
            result,
            OperationResult[bool].fail(
                "Failed to check running status for the 'package'. Code: 123.", 123
            ),
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_is_running_returns_success_of_false_on_subprocess_failure_with_code_3(
        self, mock_run: MagicMock
    ):
        """is running returns success of false on subprocess failure with code=3"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=3, cmd=""),
        ]

        # Act
        result = self.service.is_running("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(False))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_start_uses_correct_calls(self, mock_run: MagicMock):
        """start uses correct calls"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.start("package")

        # Assert
        mock_run.assert_called_once_with(
            ["systemctl", "start", "package"], stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_start_returns_success_on_successful_result(self, mock_run: MagicMock):
        """starts returns success on successful result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.start("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_start_returns_failure_on_subprocess_failure(self, mock_run: MagicMock):
        """start returns failure on subprocess failure"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.start("package")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Failed to start 'package'. Code: 123.", 123)
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_restart_uses_correct_calls(self, mock_run: MagicMock):
        """restart uses correct calls"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.restart("package")

        # Assert
        mock_run.assert_called_once_with(
            ["systemctl", "reload", "package"], stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_restart_returns_success_on_successful_result(self, mock_run: MagicMock):
        """restart returns success on successful result"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.restart("package")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_restart_returns_failure_on_subprocess_failure(self, mock_run: MagicMock):
        """restart returns failure on subprocess failure"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.restart("package")

        # Assert
        self.assertEqual(
            result, OperationResult[bool].fail("Failed to restart 'package'. Code: 123.", 123)
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_command_uses_correct_parameters_when_directory_set(self, mock_run: MagicMock):
        """execute command uses correct parameters when directory set"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.execute_command(["foo", "bar"], "/srv/docker")

        # Assert
        mock_run.assert_called_once_with(
            ["foo", "bar"], cwd="/srv/docker", stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_command_uses_correct_parameters_when_directory_not_set(
        self, mock_run: MagicMock
    ):
        """execute command uses correct parameters when directory not set"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.execute_command(["foo", "bar"])

        # Assert
        mock_run.assert_called_once_with(
            ["foo", "bar"], cwd=None, stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_command_returns_success_on_subprocess_success(self, mock_run: MagicMock):
        """execute command returns success on subprocess success"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.execute_command(["foo", "bar"], "/srv/docker")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_command_returns_failure_on_subprocess_error(self, mock_run: MagicMock):
        """execute command returns failure on subprocess error"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.execute_command(["foo", "bar"], "/srv/docker")

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Command failed. Code: 123.", 123))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_raw_command_uses_correct_parameters(self, mock_run: MagicMock):
        """execute raw command uses correct parameters"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        self.service.execute_raw_command("foo bar")

        # Assert
        mock_run.assert_called_once_with(
            ["bash", "-lc", "foo bar"], stdout=sys.stdout, stderr=sys.stderr, check=True
        )

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_raw_command_returns_success_on_subprocess_success(self, mock_run: MagicMock):
        """execute raw command returns success on subprocess success"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
        ]

        # Act
        result = self.service.execute_raw_command("foo bar")

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    @patch(f"{PACKAGE_NAME}.subprocess.run")
    def test_execute_raw_command_returns_failure_on_subprocess_error(self, mock_run: MagicMock):
        """execute raw command returns failure on subprocess error"""
        # Arrange
        mock_run.side_effect = [
            subprocess.CalledProcessError(returncode=123, cmd=""),
        ]

        # Act
        result = self.service.execute_raw_command("foo bar")

        # Assert
        self.assertEqual(result, OperationResult[bool].fail("Command failed. Code: 123.", 123))
