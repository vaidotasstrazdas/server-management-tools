from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class DockerSetupGiteaAdminUbuntuConfigurationTask(ConfigurationTask):
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
        self.notifications.info("Setting up Gitea Administrator User.")

        cmds_admin: list[str] = []

        cmds_admin.append(
            "sudo bash -lc '"
            f"if ! docker exec gitea gitea admin user list --admin 2>/dev/null | grep -qw {data.gitea_admin_login}; then "
            f"  docker exec gitea gitea admin user create --admin --username {data.gitea_admin_login} --password {data.gitea_admin_password} --email {data.gitea_admin_email} --must-change-password=false; "
            "fi'"
        )

        ensure_admin = self.controller.run_raw_commands(cmds_admin)
        if not ensure_admin.success:
            self.notifications.error(
                "\tEnsuring Gitea admin failed (will not block orchestration)."
            )
        else:
            self.notifications.success("\tGitea admin present.")

        return OperationResult[bool].succeed(True)
