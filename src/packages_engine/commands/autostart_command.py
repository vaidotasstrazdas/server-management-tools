from packages_engine.services.package_controller import PackageControllerServiceContract


class AutostartCommand:
    def __init__(self, controller: PackageControllerServiceContract):
        self.controller = controller

    def execute(self):
        self.controller.run_raw_commands(
            [
                # --- Systemd prep
                "sudo systemctl daemon-reload",
                # --- Core services (idempotent)
                "sudo systemctl enable --now nftables",
                # Ensure our host_fw table exists (only load if missing)
                'sudo nft list tables | grep -q "table inet host_fw" || sudo nft -f /etc/nftables.d/10-host-fw.nft',
                "sudo systemctl enable --now wg-quick@wg0",
                "sudo systemctl enable --now dnsmasq",
                # Split-DNS drop-in might be present; reload if so
                "test -f /etc/systemd/resolved.conf.d/10-wg-split-dns.conf && sudo systemctl reload-or-restart systemd-resolved || true",
                # --- Docker daemon is already set to After=wg-quick@wg0 via your override
                "sudo systemctl enable --now docker",
                # --- Ensure docker network exists (idempotent)
                "sudo docker network inspect vpn-internal >/dev/null 2>&1 || "
                "sudo docker network create --driver bridge --attachable vpn-internal",
                # --- Make sure data dirs exist with correct owners (safe if already set)
                "sudo install -d -m 0700 -o 999  -g 999  /srv/postgres/data",
                "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/data",
                "sudo install -d -m 0750 -o 1000 -g 1000 /srv/gitea/config",
                "sudo install -d -m 0750 -o 5050 -g 5050 /srv/pgadmin/data",
                # --- Bring the compose stack up (no pull on boot; avoid offline hang)
                "cd /srv/stack && sudo docker compose config -q",
                "cd /srv/stack && sudo docker compose up -d --remove-orphans",
                # --- Short, bounded readiness gates so we don't stall boot:
                # Wait up to ~90s for Postgres healthy
                "timeout 90 bash -lc '"
                "until [[ $(docker inspect -f {{.State.Health.Status}} postgres 2>/dev/null || echo none) == healthy ]]; "
                "do sleep 2; done' || true",
                # Probe Gitea HTTP quickly (200/301/302) but don’t fail boot if missing
                "timeout 30 bash -lc '"
                'code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/ || true); '
                "[[ $code =~ ^(200|30[12])$ ]] && exit 0 || exit 0' || true",
                # --- Nginx last, after local backends listen
                "sudo systemctl enable --now nginx",
                "sudo systemctl reload nginx || sudo systemctl restart nginx",
                # --- Optional: quick visibility without failing the unit
                "ss -lntup | grep -E '(127.0.0.1:3000|127.0.0.1:2222|127.0.0.1:5432|127.0.0.1:8081|10.10.0.1:2222|10.10.0.1:5432)' || true",
            ]
        )
