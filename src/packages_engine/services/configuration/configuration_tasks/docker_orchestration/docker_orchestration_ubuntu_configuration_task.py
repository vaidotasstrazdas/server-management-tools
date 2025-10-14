from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract

# add your primary user; for Multipass it's 'ubuntu'
# sudo usermod -aG docker ubuntu
# inform that a new login is required for the group to take effect:
# echo "Re-login or run: newgrp docker"


class DockerOrchestrationUbuntuConfigurationTask(ConfigurationTask):
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
        self.notifications.info("Orchestrating Docker containers.")
        cmds = [
            # network (only create if missing)
            "sudo docker network inspect vpn-internal >/dev/null 2>&1 || "
            "sudo docker network create --driver bridge --attachable vpn-internal",
            # daemon.json must exist first
            "sudo install -d -m 0755 /etc/docker",
            "test -f /etc/docker/daemon.json || echo '{}' | sudo tee /etc/docker/daemon.json >/dev/null",
            # merge DNS & search domain (idempotent & deduped)
            f"sudo jq --arg dns '10.10.0.1' --arg search '{data.domain_name}' "
            r"'.dns = ((.dns // []) + [$dns] | unique) | "
            r".\"dns-search\" = ((.\"dns-search\" // []) + [$search] | unique)' "
            "/etc/docker/daemon.json | sudo tee /etc/docker/daemon.json.tmp >/dev/null && "
            "sudo mv /etc/docker/daemon.json.tmp /etc/docker/daemon.json && "
            "sudo chown root:root /etc/docker/daemon.json && sudo chmod 0644 /etc/docker/daemon.json",
            # optionally ensure docker starts after wg0 so 10.10.0.1 DNS is up on boot
            "sudo install -d -m 0755 /etc/systemd/system/docker.service.d",
            "sudo bash -lc 'cat > /etc/systemd/system/docker.service.d/10-after-wg0.conf <<EOF\n[Unit]\nAfter=wg-quick@wg0.service\nWants=wg-quick@wg0.service\nEOF'",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable docker",
            "sudo systemctl restart docker",
            # compose: pull updated images and up with --remove-orphans
            "cd /srv/stack && sudo docker compose pull --quiet || true",
            "cd /srv/stack && sudo docker compose up -d --remove-orphans",
            # wait for healthchecks so subsequent tasks can rely on services being ready
            "cd /srv/stack && sudo docker compose ps",
            "cd /srv/stack && sudo docker compose wait || true",
        ]
        start_result = self.controller.run_raw_commands(cmds)
        if not start_result.success:
            self.notifications.error("\tFailed to orchestrate Docker containers.")
            return start_result.as_fail()
        self.notifications.success("\tOrchestrating Docker containers succeeded.")

        return OperationResult[bool].succeed(True)
