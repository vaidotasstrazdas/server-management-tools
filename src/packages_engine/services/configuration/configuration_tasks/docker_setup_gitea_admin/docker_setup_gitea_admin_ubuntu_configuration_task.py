"""Ubuntu configuration task for Gitea administrator setup.

This module provides a configuration task for setting up Gitea administrator users
on Ubuntu systems using Docker. It ensures the admin user exists in the Gitea container
with the specified credentials.
"""

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
    """Configuration task for setting up Gitea administrator user on Ubuntu systems.

    This task ensures that a Gitea administrator user exists in a Docker container
    running Gitea. It checks if the admin user already exists and creates it if not,
    using the credentials provided in the configuration data.
    """

    def __init__(
        self,
        reader: ConfigurationContentReaderServiceContract,
        file_system: FileSystemServiceContract,
        notifications: NotificationsServiceContract,
        controller: PackageControllerServiceContract,
    ):
        """Initialize the Gitea admin setup configuration task.

        Args:
            reader: Service for reading configuration content.
            file_system: Service for file system operations.
            notifications: Service for displaying notifications to the user.
            controller: Service for executing package controller commands.
        """
        self.reader = reader
        self.file_system = file_system
        self.notifications = notifications
        self.controller = controller

    def configure(self, data: ConfigurationData) -> OperationResult[bool]:
        """Configure Gitea administrator user in the Docker container.

        This method checks if the Gitea admin user already exists, and if not,
        creates it with the credentials specified in the configuration data.

        Args:
            data: Configuration data containing Gitea admin credentials:
                - gitea_admin_login: Admin username
                - gitea_admin_password: Admin password
                - gitea_admin_email: Admin email address

        Returns:
            OperationResult[bool]: Success result with True if admin user is ensured,
                or failure result if the operation fails.
        """
        self.notifications.info("Setting up Gitea Administrator User.")

        ensure_admin = self.controller.run_raw_commands(
            [
                "sudo bash -lc '"
                f"if ! docker exec gitea gitea admin user list --admin 2>/dev/null | grep -qw {data.gitea_admin_login}; then "
                f"  docker exec gitea gitea admin user create --admin --username {data.gitea_admin_login} --password {data.gitea_admin_password} --email {data.gitea_admin_email} --must-change-password=false; "
                "fi'"
            ]
        )
        if not ensure_admin.success:
            self.notifications.error("\tEnsuring Gitea admin failed.")
            return ensure_admin.as_fail()

        self.notifications.success("\tGitea admin present.")

        return OperationResult[bool].succeed(True)
