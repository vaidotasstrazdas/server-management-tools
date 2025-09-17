from packages_engine.models import OperationResult
from packages_engine.services.installer.installer_tasks import InstallerTask
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract
from packages_engine.services.system_management_engine import SystemManagementEngineService

class NginxUbuntuInstallerTask(InstallerTask):
    def __init__(
            self,
            notifications: NotificationsServiceContract,
            engine: SystemManagementEngineService,
            controller: PackageControllerServiceContract):
        self.notifications = notifications
        self.engine = engine
        self.controller = controller

    def install(self) -> OperationResult[bool]:
        self.notifications.info('Nginx will be installed now if it is not installed.')
        is_installed = self.engine.is_installed('nginx')
        if is_installed:
            self.notifications.success('\tNginx is installed already. Nothing needs to be done.')
            return OperationResult[bool].succeed(True)
        
        result = self.controller.run_raw_commands([
            'sudo apt update',
            'sudo apt install nginx',
            'sudo rm /etc/nginx/sites-available',
            'sudo rm /etc/nginx/sites-enabled/default',
            'sudo rm -r /var/www',
            'sudo mkdir -p /etc/ssl/internal-pki',
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out ca.key 4096',
            'cd /etc/ssl/internal-pki && sudo openssl req -x509 -new -sha256 -days 3650 -key ca.key -subj "/CN=Internal VPN CA" -out ca.crt',
            'cd /etc/ssl/internal-pki && sudo openssl genrsa -out internal.app.key 2048',
            """cd /etc/ssl/internal-pki && cat << 'EOF' | sudo tee san.cnf

[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
CN = *.internal.app

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.internal.app
DNS.2 = internal.app
EOF""",
            'cd /etc/ssl/internal-pki && sudo openssl req -new -key internal.app.key -out internal.app.csr -config san.cnf',
            'cd /etc/ssl/internal-pki && sudo openssl x509 -req -in internal.app.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out internal.app.crt -days 825 -sha256 -extensions req_ext -extfile san.cnf',
            'sudo cp /etc/ssl/internal-pki/internal.app.crt /etc/ssl/certs/internal.crt',
            'sudo cp /etc/ssl/internal-pki/internal.app.key /etc/ssl/private/internal.key',
            'sudo chown root:root /etc/ssl/certs/internal.crt /etc/ssl/private/internal.key',
            'sudo chmod 644 /etc/ssl/certs/internal.crt',
            'sudo chmod 600 /etc/ssl/private/internal.key',
            'sudo apt update',
            'sudo apt install -y libnginx-mod-stream'
        ])

        return result