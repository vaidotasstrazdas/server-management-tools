from typing import Optional

import subprocess
import sys

from packages_engine.models.operation_result import OperationResult
from packages_engine.services.system_management_engine.system_management_engine_service import SystemManagementEngineService

class LinuxUbuntuEngineService(SystemManagementEngineService):
    def is_installed(self, package: str) -> bool:
        try:
            subprocess.run(
                ["dpkg", "-s", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install(self, package: str) -> OperationResult[bool]:
        try:
            subprocess.run(
                ["sudo", "apt-get", "update"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            subprocess.run(
                ["sudo", "apt-get", "install", "-y", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(f"Failed to install '{package}'. Code: {e.returncode}.", e.returncode)

    def is_running(self, package: str) -> OperationResult[bool]:
        try:
            is_active_result = subprocess.run(
                ["systemctl", "is-active", package],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            if is_active_result == 'active':
                return OperationResult[bool].succeed(True)
            elif is_active_result == 'inactive' or is_active_result == 'failed':
                return OperationResult[bool].succeed(False)
            
            return OperationResult[bool].fail(f"Failed to check running status for the '{package}' due to unknown result returned. Result: '{is_active_result}'", 0)
        except subprocess.CalledProcessError as e:
            if e.returncode == 3:
                return OperationResult[bool].succeed(False)
            return OperationResult[bool].fail(f"Failed to check running status for the '{package}'. Code: {e.returncode}.", e.returncode)
    
    def start(self, package: str) -> OperationResult[bool]:
        try:
            subprocess.run(
                ["systemctl", "start", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(f"Failed to start '{package}'. Code: {e.returncode}.", e.returncode)
    
    def restart(self, package: str) -> OperationResult[bool]:
        try:
            subprocess.run(
                ["systemctl", "reload", package],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(f"Failed to restart '{package}'. Code: {e.returncode}.", e.returncode)
    
    def execute_command(self, command: list[str], directory: Optional[str] = None) -> OperationResult[bool]:
        try:
            subprocess.run(
                command,
                cwd=directory,
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(f"Command failed. Code: {e.returncode}.", e.returncode)

    def execute_raw_command(self, command: str) -> OperationResult[bool]:
        shell_exe = ["bash", "-lc", command]
        try:
            subprocess.run(
                shell_exe,
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
            return OperationResult[bool].succeed(True)
        except subprocess.CalledProcessError as e:
            return OperationResult[bool].fail(f"Command failed. Code: {e.returncode}.", e.returncode)