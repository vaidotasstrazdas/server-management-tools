"""Necessary imports to implement the File System Service"""

import json
from pathlib import Path

from packages_engine.models import OperationResult
from packages_engine.services.system_management import SystemManagementServiceContract

from .file_system_service_contract import FileSystemServiceContract


class FileSystemService(FileSystemServiceContract):
    """File System Service Implementation."""

    system_management_service: SystemManagementServiceContract

    def __init__(self, system_management_service: SystemManagementServiceContract):
        self.system_management_service = system_management_service

    def read_text(self, path_location: str) -> OperationResult[str]:
        check_result = self._check_path(path_location)
        if not check_result.success:
            return check_result.as_fail()
        path = self._get_path(path_location)

        text = path.read_text(encoding="utf-8")

        return OperationResult[str].succeed(text)

    def write_text(self, path_location: str, text: str) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if path.exists() and not path.is_file():
            return OperationResult[bool].fail(f"Path {path_location} is not a file")

        if not path.exists():
            absolute_path = path.absolute().as_posix()
            execute_command_result = self.system_management_service.execute_command(
                ["touch", absolute_path]
            )
            if not execute_command_result.success:
                return execute_command_result.as_fail()

        path.write_text(text, encoding="utf-8")

        return OperationResult[bool].succeed(True)

    def read_json(self, path_location: str) -> OperationResult[object]:
        check_result = self._check_path(path_location)
        if not check_result.success:
            return check_result.as_fail()
        path = self._get_path(path_location)

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return OperationResult[object].succeed(data)

        except json.JSONDecodeError:
            return OperationResult[object].fail(
                f"Error: Failed to decode JSON from the file. Path: {path_location}"
            )

    def write_json(self, path_location: str, data: object) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if path.exists() and not path.is_file():
            return OperationResult[bool].fail(f"Path {path_location} is not a file")

        if not path.exists():
            absolute_path = path.absolute().as_posix()
            execute_command_result = self.system_management_service.execute_command(
                ["touch", absolute_path]
            )
            if not execute_command_result.success:
                return execute_command_result.as_fail()
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file)
        except TypeError:
            return OperationResult[bool].fail(
                f"Failed to save JSON data into the path: {path_location}"
            )

        return OperationResult[bool].succeed(True)

    def make_dir(self, path_location: str) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if path.exists():
            if path.is_file():
                return OperationResult[bool].fail(
                    f"Path {path_location} is file, so can not make the directory out of it."
                )

            if path.is_dir():
                return OperationResult[bool].succeed(True)

            if not path.is_dir():
                return OperationResult[bool].fail(
                    f"Path {path_location} is not a file and not a directory."
                )

        absolute_path = path.absolute().as_posix()

        execute_command_result = self.system_management_service.execute_command(
            ["mkdir", "-p", absolute_path]
        )
        if not execute_command_result.success:
            return execute_command_result.as_fail()

        return OperationResult[bool].succeed(True)

    def chmod(self, path_location: str, chmod: int) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if not path.exists():
            return OperationResult[bool].fail(f"Path {path_location} does not exist.")
        absolute_path = path.absolute().as_posix()
        return self.system_management_service.execute_command(["chmod", str(chmod), absolute_path])

    def remove_location(self, path_location: str) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if not path.exists():
            return OperationResult[bool].succeed(True)

        absolute_path = path.absolute().as_posix()

        if path.is_file():
            return self.system_management_service.execute_command(["rm", absolute_path])

        if path.is_dir():
            return self.system_management_service.execute_command(["rm", "-r", absolute_path])

        return OperationResult[bool].fail(
            f"Location {path_location} is neither file nor directory."
        )

    def path_exists(self, path_location: str) -> bool:
        path = self._get_path(path_location)
        return path.exists()

    def copy_path(self, location_from: str, location_to: str) -> OperationResult[bool]:
        if not self.path_exists(location_from):
            return OperationResult[bool].fail(f'Path "{location_from}" does not exist')

        if self.path_exists(location_to):
            remove_result = self.remove_location(location_to)
            if not remove_result.success:
                return remove_result.as_fail()

        execute_raw_command_result = self.system_management_service.execute_raw_command(
            f"sudo mkdir -p {location_to} && sudo cp -a {location_from} {location_to}"
        )

        if not execute_raw_command_result.success:
            return execute_raw_command_result.as_fail()

        return OperationResult[bool].succeed(True)

    def _get_path(self, path_location: str) -> Path:
        return Path(path_location)

    def _check_path(self, path_location: str) -> OperationResult[bool]:
        path = self._get_path(path_location)
        if not path.exists():
            return OperationResult[bool].fail(f"Path {path_location} does not exist")

        if not path.is_file():
            return OperationResult[bool].fail(f"Path {path_location} is not a file")

        return OperationResult[bool].succeed(True)
