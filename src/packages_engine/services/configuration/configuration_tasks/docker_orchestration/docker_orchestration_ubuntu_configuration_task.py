from packages_engine.models import OperationResult
from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.configuration.configuration_content_reader import (
    ConfigurationContentReaderServiceContract,
)
from packages_engine.services.configuration.configuration_tasks import ConfigurationTask
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.notifications import NotificationsServiceContract
from packages_engine.services.package_controller import PackageControllerServiceContract


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
            '\'.dns = ((.dns // []) + [$dns] | unique) | ."dns-search" = ((."dns-search" // []) + [$search] | unique)\' '
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
            "cd /srv/stack && sudo docker compose config -q",
            "cd /srv/stack && sudo docker compose up -d --remove-orphans",
            # wait for healthchecks so subsequent tasks can rely on services being ready
            "cd /srv/stack && sudo docker compose ps",
            "timeout 120 bash -lc '"
            '  echo "Waiting for Postgres health=healthy…";'
            "  until [[ $(docker inspect -f {{.State.Health.Status}} postgres 2>/dev/null || echo none) == healthy ]]; do sleep 2; done;"
            '  echo "Postgres is healthy. Probing Gitea on 127.0.0.1:3000…";'
            "  for i in {1..60}; do "
            '    code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/ || true); '
            '    if [[ $code =~ ^(200|30[12])$ ]]; then echo "Gitea is responding ($code)."; exit 0; fi; '
            "    sleep 2; "
            "  done; "
            '  echo "Gitea did not respond with 200/301/302 within timeout; continuing anyway.";'
            "' || true",
            # show ports bound to loopback (host side)
            "ss -lntup | grep -E '(:5432|:3000|:2222|:8081)\\b' || true",
            # DNS smoke test from a throwaway container via Docker’s embedded DNS
            f"sudo docker run --rm --network vpn-internal busybox sh -lc "
            f"'nslookup gitea.{data.domain_name} 127.0.0.11 && nslookup postgresql.{data.domain_name} 127.0.0.11' || true",
        ]
        start_result = self.controller.run_raw_commands(cmds)
        if not start_result.success:
            self.notifications.error("\tFailed to orchestrate Docker containers.")
            return start_result.as_fail()
        self.notifications.success("\tOrchestrating Docker containers succeeded.")

        return OperationResult[bool].succeed(True)
