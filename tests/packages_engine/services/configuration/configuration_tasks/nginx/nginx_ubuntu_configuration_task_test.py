import unittest

from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationContent, ConfigurationData
from packages_engine.services.configuration.configuration_content_reader.configuration_content_reader_service_mock import (
    MockConfigurationContentReaderService,
    ReadParams,
)
from packages_engine.services.configuration.configuration_tasks.nginx import (
    NginxUbuntuConfigurationTask,
)
from packages_engine.services.file_system.file_system_service_mock import (
    MockFileSystemService,
)
from packages_engine.services.notifications.notifications_service_mock import (
    MockNotificationsService,
)
from packages_engine.services.package_controller.package_controller_service_mock import (
    MockPackageControllerService,
)


class TestNginxUbuntuConfigurationTask(unittest.TestCase):
    reader: MockConfigurationContentReaderService
    file_system: MockFileSystemService
    notifications: MockNotificationsService
    controller: MockPackageControllerService
    task: NginxUbuntuConfigurationTask
    data: ConfigurationData

    def setUp(self):
        self.reader = MockConfigurationContentReaderService()
        self.file_system = MockFileSystemService()
        self.notifications = MockNotificationsService()
        self.controller = MockPackageControllerService()
        self.task = NginxUbuntuConfigurationTask(
            self.reader, self.file_system, self.notifications, self.controller
        )
        self.data = ConfigurationData.default()
        self.data.server_data_dir = "srv"
        self.reader.read_result_map = {
            "/usr/local/share/srv/data/nginx/sites-available/gitea.app": OperationResult[
                str
            ].succeed("gitea.app config template"),
            "/usr/local/share/srv/data/nginx/sites-available/postgresql.app": OperationResult[
                str
            ].succeed("postgresql.app config template"),
            "/usr/local/share/srv/data/nginx/nginx.conf": OperationResult[str].succeed(
                "nginx.conf config template"
            ),
        }
        self.file_system.write_text_result_map = {
            "/etc/nginx/sites-available/gitea.app": OperationResult[bool].succeed(True),
            "/etc/nginx/sites-available/postgresql.app": OperationResult[bool].succeed(True),
            "/etc/nginx/nginx.conf": OperationResult[bool].succeed(True),
        }
        self.maxDiff = None

    def test_happy_path(self):
        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))

    def test_happy_path_produces_correct_notifications_flow(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring Nginx.", "type": "info"},
                {"text": "Replacing Nginx configurations.", "type": "info"},
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' to "
                    "'/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' to "
                    "'/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' to "
                    "'/etc/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' successful.",
                    "type": "success",
                },
                {"text": "Saving config data to '/etc/nginx/nginx.conf'.", "type": "info"},
                {
                    "text": "Saving config data to '/etc/nginx/nginx.conf' successful.",
                    "type": "success",
                },
                {"text": "Replacing Nginx configurations successful.", "type": "success"},
                {"text": "Restarting Nginx.", "type": "info"},
                {"text": "Enabling sites and validating Nginx config.", "type": "info"},
                {"text": "Loading Nginx configuration successful.", "type": "success"},
            ],
        )

    def test_reads_nginx_configuration_templates(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.reader.read_params,
            [
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/nginx/sites-available/gitea.app",
                ),
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/nginx/sites-available/postgresql.app",
                ),
                ReadParams(
                    ConfigurationContent.RAW_STRING,
                    self.data,
                    "/usr/local/share/srv/data/nginx/nginx.conf",
                ),
            ],
        )

    def test_failure_to_read_gitea_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map["/usr/local/share/srv/data/nginx/sites-available/gitea.app"] = (
            failure_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_gitea_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map["/usr/local/share/srv/data/nginx/sites-available/gitea.app"] = (
            failure_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("gitea.app")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' to "
                    "'/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_read_postgresql_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map[
            "/usr/local/share/srv/data/nginx/sites-available/postgresql.app"
        ] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_postgresql_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map[
            "/usr/local/share/srv/data/nginx/sites-available/postgresql.app"
        ] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("postgresql.app")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' to "
                    "'/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' "
                    "failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_read_nginx_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map["/usr/local/share/srv/data/nginx/nginx.conf"] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_read_nginx_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[str].fail("Failure")
        self.reader.read_result_map["/usr/local/share/srv/data/nginx/nginx.conf"] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("nginx.conf")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' to "
                    "'/etc/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_store_gitea_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/sites-available/gitea.app"] = (
            failure_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_gitea_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/sites-available/gitea.app"] = (
            failure_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("gitea.app")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' to "
                    "'/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app' "
                    "failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_store_postgresql_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/sites-available/postgresql.app"] = (
            failure_result
        )

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_postgresql_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/sites-available/postgresql.app"] = (
            failure_result
        )

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("postgresql.app")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' to "
                    "'/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app' "
                    "failed.",
                    "type": "error",
                },
            ],
        )

    def test_failure_to_store_nginx_config_result_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/nginx.conf"] = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_store_nginx_config_result_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.file_system.write_text_result_map["/etc/nginx/nginx.conf"] = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        related_notifications = self.notifications.find_notifications("nginx.conf")
        self.assertEqual(
            related_notifications,
            [
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' to "
                    "'/etc/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' successful.",
                    "type": "success",
                },
                {"text": "Saving config data to '/etc/nginx/nginx.conf'.", "type": "info"},
                {"text": "Saving config data to '/etc/nginx/nginx.conf' failed.", "type": "error"},
            ],
        )

    def test_runs_configuration_commands(self):
        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.controller.run_raw_commands_params,
            [
                [
                    "sudo install -d -m 0755 /etc/nginx/sites-enabled",
                    "sudo rm -f /etc/nginx/sites-enabled/default",
                    "sudo ln -sf /etc/nginx/sites-available/gitea.app /etc/nginx/sites-enabled/gitea.app",
                    "sudo ln -sf /etc/nginx/sites-available/postgresql.app /etc/nginx/sites-enabled/postgresql.app",
                    "sudo nginx -t -q",
                    "sudo systemctl reload nginx || sudo systemctl restart nginx || sudo service nginx restart || sudo service nginx start",
                ]
            ],
        )

    def test_failure_to_run_commands_results_in_failure(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = failure_result

        # Act
        result = self.task.configure(self.data)

        # Assert
        self.assertEqual(result, failure_result)

    def test_failure_to_run_commands_results_in_failure_notifications_flow(self):
        # Arrange
        failure_result = OperationResult[bool].fail("Failure")
        self.controller.run_raw_commands_result = failure_result

        # Act
        self.task.configure(self.data)

        # Assert
        self.assertEqual(
            self.notifications.params,
            [
                {"text": "Configuring Nginx.", "type": "info"},
                {"text": "Replacing Nginx configurations.", "type": "info"},
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' to "
                    "'/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/gitea.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/gitea.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' to "
                    "'/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/sites-available/postgresql.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app'.",
                    "type": "info",
                },
                {
                    "text": "Saving config data to '/etc/nginx/sites-available/postgresql.app' "
                    "successful.",
                    "type": "success",
                },
                {
                    "text": "Saving configuration from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' to "
                    "'/etc/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf'.",
                    "type": "info",
                },
                {
                    "text": "Loading config template from "
                    "'/usr/local/share/srv/data/nginx/nginx.conf' successful.",
                    "type": "success",
                },
                {"text": "Saving config data to '/etc/nginx/nginx.conf'.", "type": "info"},
                {
                    "text": "Saving config data to '/etc/nginx/nginx.conf' successful.",
                    "type": "success",
                },
                {"text": "Replacing Nginx configurations successful.", "type": "success"},
                {"text": "Restarting Nginx.", "type": "info"},
                {"text": "Enabling sites and validating Nginx config.", "type": "info"},
                {"text": "Loading Nginx configuration  Nginx failed.", "type": "error"},
            ],
        )
