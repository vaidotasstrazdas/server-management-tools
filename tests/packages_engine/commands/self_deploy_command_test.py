import unittest

from packages_engine.models import OperationResult
from packages_engine.services.file_system.file_system_service_mock import MockFileSystemService
from packages_engine.services.file_system.file_system_service_mock import CopyPathParams
from packages_engine.services.input_collection.input_collection_service_mock import MockInputCollectionService
from packages_engine.services.input_collection.input_collection_service_mock import ReadParams
from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.commands import SelfDeployCommand


class TestSelfDeployCommand(unittest.TestCase):
    file_system: MockFileSystemService
    input_collection: MockInputCollectionService
    notifications: MockNotificationsService
    command: SelfDeployCommand

    def setUp(self):
        self.file_system = MockFileSystemService()
        self.input_collection = MockInputCollectionService()
        self.notifications = MockNotificationsService()
        self.command = SelfDeployCommand(
            self.file_system, self.input_collection, self.notifications
        )
        self.input_collection.read_str_result = 'srv'
        self.maxDiff = None

    def test_happy_path_has_correct_notifications(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {'text': 'Will check paths if self deployment possible', 'type': 'info'},
                {'text': 'Copying from "data/." to "/usr/local/share/srv/data"',
                    'type': 'info'},
                {'text': '\tCopying from "data/." to "/usr/local/share/srv/data" successful',
                    'type': 'success'},
                {'text': 'Copying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz" '
                    'successful',
                    'type': 'success'},
                {'text': 'Copying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz" successful',
                    'type': 'success'},
                {'text': 'Copying from "installer.pyz" to "/usr/local/sbin/installer.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "installer.pyz" to "/usr/local/sbin/installer.pyz" '
                    'successful',
                    'type': 'success'}
            ]
        )

    def test_checks_for_paths(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.file_system.path_exists_params,
            ['data', 'autostart.pyz', 'configurator.pyz', 'installer.pyz']
        )

    def test_copies_paths(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.file_system.copy_path_params,
            [
                CopyPathParams(
                    location_from='data/.',
                    location_to='/usr/local/share/srv/data'
                ),
                CopyPathParams(
                    location_from='autostart.pyz',
                    location_to='/usr/local/sbin/autostart.pyz'
                ),
                CopyPathParams(
                    location_from='configurator.pyz',
                    location_to='/usr/local/sbin/configurator.pyz'
                ),
                CopyPathParams(
                    location_from='installer.pyz',
                    location_to='/usr/local/sbin/installer.pyz'
                )
            ]
        )

    def test_reads_server_data_directory(self):
        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.input_collection.read_str_params,
            [
                ReadParams[str]('Server data directory', 'srv', 1)
            ]
        )

    def test_correct_notifications_visible_when_path_does_not_exist_case_1(self):
        self._path_existence_fail_notifications_test(
            'data'
        )

    def test_correct_notifications_visible_when_path_does_not_exist_case_2(self):
        self._path_existence_fail_notifications_test(
            'autostart.pyz'
        )

    def test_correct_notifications_visible_when_path_does_not_exist_case_3(self):
        self._path_existence_fail_notifications_test(
            'configurator.pyz'
        )

    def test_correct_notifications_visible_when_path_does_not_exist_case_4(self):
        self._path_existence_fail_notifications_test(
            'installer.pyz'
        )

    def test_correct_notifications_visible_on_copy_failure_case_1(self):
        self._copy_fail_notifications_test(
            'data/.->/usr/local/share/srv/data',
            [
                {'text': 'Will check paths if self deployment possible', 'type': 'info'},
                {'text': 'Copying from "data/." to "/usr/local/share/srv/data"',
                    'type': 'info'},
                {'text': '\tCopying from "data/." to "/usr/local/share/srv/data" failed',
                    'type': 'error'}
            ]
        )

    def test_correct_notifications_visible_on_copy_failure_case_2(self):
        self._copy_fail_notifications_test(
            'autostart.pyz->/usr/local/sbin/autostart.pyz',
            [
                {'text': 'Will check paths if self deployment possible', 'type': 'info'},
                {'text': 'Copying from "data/." to "/usr/local/share/srv/data"',
                    'type': 'info'},
                {'text': '\tCopying from "data/." to "/usr/local/share/srv/data" successful',
                    'type': 'success'},
                {'text': 'Copying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz" '
                    'failed',
                    'type': 'error'}
            ]
        )

    def test_correct_notifications_visible_on_copy_failure_case_3(self):
        self._copy_fail_notifications_test(
            'configurator.pyz->/usr/local/sbin/configurator.pyz',
            [
                {'text': 'Will check paths if self deployment possible', 'type': 'info'},
                {'text': 'Copying from "data/." to "/usr/local/share/srv/data"',
                    'type': 'info'},
                {'text': '\tCopying from "data/." to "/usr/local/share/srv/data" successful',
                    'type': 'success'},
                {'text': 'Copying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz" '
                    'successful',
                    'type': 'success'},
                {'text': 'Copying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz" failed',
                    'type': 'error'}
            ]
        )

    def test_correct_notifications_visible_on_copy_failure_case_4(self):
        self._copy_fail_notifications_test(
            'installer.pyz->/usr/local/sbin/installer.pyz',
            [
                {'text': 'Will check paths if self deployment possible', 'type': 'info'},
                {'text': 'Copying from "data/." to "/usr/local/share/srv/data"',
                    'type': 'info'},
                {'text': '\tCopying from "data/." to "/usr/local/share/srv/data" successful',
                    'type': 'success'},
                {'text': 'Copying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "autostart.pyz" to "/usr/local/sbin/autostart.pyz" '
                    'successful',
                    'type': 'success'},
                {'text': 'Copying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "configurator.pyz" to '
                    '"/usr/local/sbin/configurator.pyz" successful',
                    'type': 'success'},
                {'text': 'Copying from "installer.pyz" to "/usr/local/sbin/installer.pyz"',
                    'type': 'info'},
                {'text': '\tCopying from "installer.pyz" to "/usr/local/sbin/installer.pyz" '
                    'failed',
                    'type': 'error'}
            ]
        )

    def _path_existence_fail_notifications_test(self, path: str):
        # Arrange
        self.file_system.path_exists_result_map[path] = False

        # Act
        self.command.execute()

        # Assert
        expected_notifications = [
            {'text': 'Will check paths if self deployment possible', 'type': 'info'},
            {'text': f'Path {path} does not exist, probably this is not the path where self deployment should start from.', 'type': 'error'}
        ]
        self.assertEqual(
            self.notifications.params,
            expected_notifications
        )

    def _copy_fail_notifications_test(self, copy_sequence: str, expected_notifications: list[object]):
        # Arrange
        self.file_system.copy_path_result_map[copy_sequence] = OperationResult[bool].fail(
            'Failure')

        # Act
        self.command.execute()

        # Assert
        self.assertEqual(
            self.notifications.params,
            expected_notifications
        )
