import unittest

from packages_engine.models import OperationResult

from packages_engine.services.notifications.notifications_service_mock import MockNotificationsService
from packages_engine.services.package_controller.package_controller_service_mock import MockPackageControllerService
from packages_engine.services.system_management_engine.system_management_engine_service_mock import MockSystemManagementEngineService
from packages_engine.services.installer.installer_tasks.nginx import NginxUbuntuInstallerTask

class TestNginxUbuntuInstallerTask(unittest.TestCase):
    notifications: MockNotificationsService
    engine: MockSystemManagementEngineService
    controller: MockPackageControllerService
    task: NginxUbuntuInstallerTask

    def setUp(self):
        self.notifications = MockNotificationsService()
        self.engine = MockSystemManagementEngineService()
        self.controller = MockPackageControllerService()
        self.task = NginxUbuntuInstallerTask(self.notifications, self.engine, self.controller)
    
    def test_checks_for_nginx_installation_status(self):
        # Act
        self.task.install()

        # Assert
        params = self.engine.is_installed_params
        self.assertEqual(params, ['nginx'])

    def test_notification_flow_when_nginx_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Nginx will be installed now if it is not installed.'},
                {'type':'success','text':'\tNginx is installed already. Nothing needs to be done.'},
            ]
        )

    def test_notification_flow_when_nginx_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.notifications.params
        self.assertEqual(
            params,
            [
                {'type':'info','text':'Nginx will be installed now if it is not installed.'}
            ]
        )

    def test_no_commands_executed_when_nginx_installed_already(self):
        # Arrange
        self.engine.is_installed_result = True

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(params, [])

    def test_correct_commands_executed_when_nginx_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False

        # Act
        self.task.install()

        # Assert
        params = self.controller.run_raw_commands_params
        self.assertEqual(
            params,
            [
                [
                    'sudo apt update',
                    'sudo apt install nginx',
                    'sudo rm /etc/nginx/sites-available',
                    'sudo rm /etc/nginx/sites-enabled/default',
                    'sudo rm -r /var/www',
                    'sudo mkdir -p /etc/ssl/internal-pki',
                    'cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096',
                    'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt',
                    'cd /etc/ssl/internal-pki && sudo openssl genrsa -out {{DOMAIN_NAME}}.key 2048',
                    """cd /etc/ssl/internal-pki && cat << 'EOF' | sudo tee san.cnf

[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
CN = *.{{DOMAIN_NAME}}

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.{{DOMAIN_NAME}}
DNS.2 = {{DOMAIN_NAME}}
EOF""",
                    'cd /etc/ssl/internal-pki && sudo openssl req -new -key {{DOMAIN_NAME}}.key -out {{DOMAIN_NAME}}.csr -config san.cnf',
                    'cd /etc/ssl/internal-pki && sudo openssl x509 -req -in {{DOMAIN_NAME}}.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out {{DOMAIN_NAME}}.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf',
                    'sudo cp /etc/ssl/internal-pki/{{DOMAIN_NAME}}.crt /etc/ssl/certs/internal.crt',
                    'sudo cp /etc/ssl/internal-pki/{{DOMAIN_NAME}}.key /etc/ssl/private/internal.key',
                    'sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key',
                    'sudo chmod 644 /etc/ssl/certs/internal.crt',
                    'sudo chmod 600 /etc/ssl/private/internal.key',
                    'sudo apt update',
                    'sudo apt install -y libnginx-mod-stream'
                ]
            ]
        )

    def test_returns_result_from_packages_controller_when_nginx_not_installed(self):
        # Arrange
        self.engine.is_installed_result = False
        self.controller.run_raw_commands_result = OperationResult[bool].succeed(True)

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, self.controller.run_raw_commands_result)

    def test_returns_success_result_when_nginx_installed(self):
        # Arrange
        self.engine.is_installed_result = True
        self.controller.run_raw_commands_result = OperationResult[bool].fail('failure')

        # Act
        result = self.task.install()

        # Assert
        self.assertEqual(result, OperationResult[bool].succeed(True))