from typing import Any

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


class NginxUbuntuConfigurationTask(ConfigurationTask):
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
        self.notifications.info("Configuring Nginx.")

        self.notifications.info("Replacing Nginx configurations.")
        store_result = self._store_configurations(
            data,
            [
                {
                    "template_path": f"/usr/local/share/{data.server_data_dir}/data/nginx/sites-available/gitea.app",
                    "destination_path": "/etc/nginx/sites-available/gitea.app",
                },
                {
                    "template_path": f"/usr/local/share/{data.server_data_dir}/data/nginx/sites-available/postgresql.app",
                    "destination_path": "/etc/nginx/sites-available/postgresql.app",
                },
                {
                    "template_path": f"/usr/local/share/{data.server_data_dir}/data/nginx/nginx.conf",
                    "destination_path": "/etc/nginx/nginx.conf",
                },
            ],
        )
        if not store_result.success:
            self.notifications.error("Replacing Nginx configurations failed.")
            return store_result.as_fail()

        self.notifications.success("Replacing Nginx configurations successful.")
        self.notifications.info("Restarting Nginx.")

        self.notifications.info("Enabling sites and validating Nginx config.")
        command_result = self.controller.run_raw_commands(
            [
                "sudo install -d -m 0755 /etc/nginx/sites-enabled",
                "sudo rm -f /etc/nginx/sites-enabled/default",
                "sudo ln -sf /etc/nginx/sites-available/gitea.app /etc/nginx/sites-enabled/gitea.app",
                "sudo ln -sf /etc/nginx/sites-available/postgresql.app /etc/nginx/sites-enabled/postgresql.app",
                "sudo nginx -t -q",
                "sudo systemctl reload nginx || sudo systemctl restart nginx || sudo service nginx restart || sudo service nginx start",
            ]
        )

        if not command_result.success:
            self.notifications.error("Loading Nginx configuration  Nginx failed.")
            return command_result.as_fail()
        self.notifications.success("Loading Nginx configuration successful.")

        return OperationResult[bool].succeed(True)

    def _store_configurations(
        self, data: ConfigurationData, sites: list[Any]
    ) -> OperationResult[bool]:
        for site in sites:
            store_result = self._store_configuration(data, site)
            if not store_result.success:
                return store_result.as_fail()

        return OperationResult[bool].succeed(True)

    def _store_configuration(
        self, data: ConfigurationData, site_config: Any
    ) -> OperationResult[bool]:
        template_path = site_config["template_path"]
        destination_path = site_config["destination_path"]
        self.notifications.info(
            f"Saving configuration from '{template_path}' to '{destination_path}'."
        )
        self.notifications.info(f"Loading config template from '{template_path}'.")
        config_template_read_result = self.reader.read(
            ConfigurationContent.RAW_STRING,
            data,
            template_path,
        )

        if not config_template_read_result.success or config_template_read_result.data is None:
            self.notifications.error(f"Loading config template from '{template_path}' failed.")
            return config_template_read_result.as_fail()
        self.notifications.success(f"Loading config template from '{template_path}' successful.")

        self.notifications.info(f"Saving config data to '{destination_path}'.")
        config_save_result = self.file_system.write_text(
            destination_path, config_template_read_result.data
        )

        if not config_save_result.success or config_save_result.data is None:
            self.notifications.error(f"Saving config data to '{destination_path}' failed.")
            return config_save_result.as_fail()

        self.notifications.success(f"Saving config data to '{destination_path}' successful.")

        return OperationResult[bool].succeed(True)
