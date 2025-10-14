from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class DockerResourcesUbuntuConfigurationTask(ConfigurationTask):
    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        self.notifications.info("Creating Docker folders if they do not exist.")
        # ensure directories exist with correct perms/owners
        fix_dirs = self.controller.run_raw_commands(
            [
                # stack folder
                "sudo install -d -m 0755 /srv/stack",
                # postgres (UID:GID 999:999 is what the official image uses)
                "sudo install -d -m 0700 -o 999 -g 999 /srv/postgres/data",
                # gitea (rootless: 1000:1000; separate data and config)
                "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/data",
                "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config",
                # pgadmin (5050:5050)
                "sudo install -d -m 0750 -o 5050 -g 5050 /srv/pgadmin/data",
            ]
        )
        if not fix_dirs.success:
            self.notifications.error("Failed creating Docker folders.")
            return fix_dirs.as_fail()
        self.notifications.success("Creating Docker folders successful.")

        self.notifications.info("Reading Docker Config template data.")
        read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/docker-compose.yml",
        )

        if not read_result.success or read_result.data is None:
            self.notifications.error("\tReading Docker Config template data failed.")
            return read_result.as_fail()
        self.notifications.success("\tReading Docker Config template data succeeded.")

        self.notifications.info("Writing Docker configuration.")
        write_result = self.file_system.write_text(
            "/srv/stack/docker-compose.yml", read_result.data
        )
        if not write_result.success:
            self.notifications.error("\tWriting Docker configuration failed.")
            return write_result.as_fail()
        self.notifications.success("\tWriting Docker configuration succeeded.")

        self.notifications.info("Fixing Docker configuration permissions.")
        perm_res = self.controller.run_raw_commands(
            [
                "sudo chown root:root /srv/stack/docker-compose.yml",
                "sudo chmod 0644 /srv/stack/docker-compose.yml",
            ]
        )
        if not perm_res.success:
            self.notifications.error("Fixing Docker configuration permissions failed.")
            return perm_res.as_fail()
        self.notifications.success("Fixing Docker configuration permissions successful.")

        return OperationResult[bool].succeed(True)
