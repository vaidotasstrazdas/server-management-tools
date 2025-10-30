from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class DockerSeedGiteaUbuntuConfigurationTask(ConfigurationTask):
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
        self.notifications.info("Seeding Gitea app.ini if missing.")

        gitea_ini_path = "/srv/gitea/config/app.ini"
        self.notifications.info("Will check Gitea configuration and create it if needed.")
        if self.file_system.path_exists(gitea_ini_path):
            self.notifications.success(
                "\tGitea configuration exists already. Nothing needs to be done."
            )
            return OperationResult[bool].succeed(True)

        self.notifications.info("Will read Gitea configurations template.")
        appini_tmpl = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            f"/usr/local/share/{data.server_data_dir}/data/gitea/app.ini",
        )

        if not appini_tmpl.success or appini_tmpl.data is None:
            self.notifications.error("\tFailed to read gitea/app.ini template.")
            return appini_tmpl.as_fail()
        self.notifications.success("\tReading Gitea configurations template succeeded.")

        self.notifications.info("Will install Gitea path if it does not exist.")
        install_result = self.controller.run_raw_commands(
            ["umask 0137 && install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config"]
        )
        if not install_result.success:
            self.notifications.error("\tInstall failed.")
            return install_result.as_fail()
        self.notifications.success("\tInstall succeeded.")

        self.notifications.info("Gitea configuration does not exist. Will create it now.")
        write_result = self.file_system.write_text(gitea_ini_path, appini_tmpl.data)
        if not write_result.success:
            self.notifications.error("\tFailed storing Gitea configuration.")
            return write_result.as_fail()
        self.notifications.success("\tSucceeded in saving Gitea configuration.")

        self.notifications.info("Will process Gitea permissions.")
        process_result = self.controller.run_raw_commands(
            [
                "sudo chown 1000:1000 /srv/gitea/config/app.ini && sudo chmod 0640 /srv/gitea/config/app.ini"
            ]
        )
        if not process_result.success:
            self.notifications.error("\tProcessing failed.")
            return process_result.as_fail()
        self.notifications.success("\tProcessing succeeded.")

        return OperationResult[bool].succeed(True)
