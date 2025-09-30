from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.input_collection import InputCollectionServiceContract
from packages_engine.services.notifications import NotificationsServiceContract


class SelfDeployCommand:
    def __init__(self,
                 file_system: FileSystemServiceContract,
                 input_collection: InputCollectionServiceContract,
                 notifications: NotificationsServiceContract):
        self.file_system = file_system
        self.input_collection = input_collection
        self.notifications = notifications

    def execute(self):
        check_result = self._check_paths([
            'data',
            'autostart.pyz',
            'configurator.pyz',
            'installer.pyz'
        ])
        if not check_result:
            return

        server_data_dir = self.input_collection.read_str(
            'Server data directory', 'srv'
        )
        data_location = f'/usr/local/share/{server_data_dir}/data'
        scripts_location = '/usr/local/sbin'
        self._copy_paths(
            [
                'data/.',
                'autostart.pyz',
                'configurator.pyz',
                'installer.pyz'
            ],
            [
                data_location,
                f'{scripts_location}/autostart.pyz',
                f'{scripts_location}/configurator.pyz',
                f'{scripts_location}/installer.pyz'
            ]
        )

    def _check_paths(self, paths: list[str]) -> bool:
        self.notifications.info('Will check paths if self deployment possible')
        for path in paths:
            path_exists = self.file_system.path_exists(path)
            if not path_exists:
                self.notifications.error(
                    f'Path {path} does not exist, probably this is not the path where self deployment should start from.'
                )
                return False
        return True

    def _copy_paths(self, paths_from: list[str], paths_to: list[str]):
        for i in range(0, len(paths_from)):
            path_from = paths_from[i]
            path_to = paths_to[i]
            self.notifications.info(
                f'Copying from "{path_from}" to "{path_to}"'
            )
            copy_result = self.file_system.copy_path(path_from, path_to)
            if not copy_result.success:
                self.notifications.error(
                    f'\tCopying from "{path_from}" to "{path_to}" failed'
                )
                return
            else:
                self.notifications.success(
                    f'\tCopying from "{path_from}" to "{path_to}" successful'
                )
