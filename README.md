# Server Management Tools

Automated Python-based toolkit for setting up and managing a self-hosted Ubuntu Linux home server with VPN, DNS, containerized services, and TLS encryption.

## Overview

This project automates the deployment of a complete internal infrastructure including:

- **WireGuard VPN** for secure remote access
- **Dnsmasq** for internal DNS resolution
- **NFTables** firewall with restrictive rules
- **Docker services**: Gitea (Git hosting), PostgreSQL, pgAdmin
- **Nginx** reverse proxy with TLS termination
- **Internal PKI** with self-signed CA and certificates

All services are bound to localhost and only accessible via VPN. The system uses template-based configuration with automatic service orchestration.

## Disclaimer

This solution is designed for personal home server use and educational purposes. It is **not production-ready** for environments requiring high security, stability, or scalability. Use at your own risk.

## Requirements

- Ubuntu Linux (tested on Ubuntu Server)
- Python 3.11 or higher
- Root access (sudo)

## Available Commands

The project provides four main commands built as Python zipapps (.pyz):

### 1. `installer.pyz`

Installs all required system packages and dependencies.

**Installation order:**

1. System setup (directories, repositories)
2. WireGuard (VPN server)
3. Dnsmasq (DNS server)
4. NFTables (firewall)
5. Docker (Engine, Compose, BuildX)
6. Nginx (web server)
7. Post-install verification

### 2. `configurator.pyz`

Configures all services with user-provided settings (interactive).

**Configuration tasks:**

1. Firewall rules (NFTables)
2. DNS server (Dnsmasq)
3. VPN keys and peers (WireGuard)
4. Service management (systemd)
5. Docker resources (networks, volumes)
6. Gitea initialization and admin setup
7. SSL/TLS certificates (internal CA)
8. Reverse proxy (Nginx)
9. Autostart service

### 3. `autostart.pyz`

Starts all services in the correct dependency order. Configured to run on system boot.

**Startup sequence:**

- Load firewall rules
- Start WireGuard VPN
- Start DNS server
- Start Docker and containers
- Wait for service health checks
- Start Nginx reverse proxy

### 4. `self_deploy.pyz`

Deploys the built tools and data files to system directories.

**Deployment locations:**

- Tools: `/usr/local/sbin/`
- Data: `/usr/local/share/{server_data_dir}/data`

## Configuration Variables

When running `configurator.pyz`, you will be prompted for the following settings. Most have defaults for quick testing, but **you should change them for production use**.

### Server Data

| Configuration Key | Purpose                                                                                | Default Value | Required |
| ----------------- | -------------------------------------------------------------------------------------- | ------------- | -------- |
| SERVER_DATA_DIR   | Directory where deployed data files will be stored                                     | srv           | Yes      |
| REMOTE_IP_ADDRESS | Your external IP address for WireGuard VPN endpoint (check with whatismyipaddress.com) | -             | Yes      |

### DNS

| Configuration Key | Purpose                                                                                      | Default Value | Required |
| ----------------- | -------------------------------------------------------------------------------------------- | ------------- | -------- |
| DOMAIN_NAME       | Internal domain for accessing services (e.g., `internal.app` → `https://gitea.internal.app`) | internal.app  | Yes      |

### Gitea (Git Hosting)

| Configuration Key    | Purpose                            | Default Value     | Required |
| -------------------- | ---------------------------------- | ----------------- | -------- |
| GITEA_DB_NAME        | PostgreSQL database name for Gitea | gitea             | Yes      |
| GITEA_DB_USER        | PostgreSQL user for Gitea          | gitea             | Yes      |
| GITEA_DB_PASSWORD    | PostgreSQL user password for Gitea | 123456            | Yes      |
| GITEA_ADMIN_LOGIN    | Gitea administrator username       | admin             | Yes      |
| GITEA_ADMIN_EMAIL    | Gitea administrator email          | admin@example.com | Yes      |
| GITEA_ADMIN_PASSWORD | Gitea administrator password       | 123456            | Yes      |
| GITEA_SECRET_KEY     | Gitea internal secret key          | secret-key        | Yes      |

### PostgreSQL

| Configuration Key | Purpose                | Default Value    | Required |
| ----------------- | ---------------------- | ---------------- | -------- |
| PG_ADMIN_EMAIL    | pgAdmin login email    | user@example.com | Yes      |
| PG_ADMIN_PASSWORD | pgAdmin login password | 123456           | Yes      |

### WireGuard VPN

| Configuration Key      | Purpose                                                                  | Default Value | Required |
| ---------------------- | ------------------------------------------------------------------------ | ------------- | -------- |
| NUM_WIREGUARD_CLIENTS  | Number of VPN client configurations to generate                          | 2             | Yes      |
| WIREGUARD_CLIENT_NAMES | Names for each VPN client (e.g., laptop, phone)                          | []            | Yes      |
| CLIENTS_DATA_DIR       | Directory path where client VPN configs and CA certificate will be saved | -             | Yes      |

**Note:** The following are auto-generated during configuration:

- `SERVER_KEY` - WireGuard server private key
- `CLIENT_PUBLIC_KEY` - Client public keys
- `CLIENT_IP_ADDRESS` - Client IPs in VPN (10.10.0.2, 10.10.0.3, etc.)

## Services Deployed

### Docker Stack (docker-compose.yml)

| Service    | Image                     | Ports                 | Access URL                       | Purpose                 |
| ---------- | ------------------------- | --------------------- | -------------------------------- | ----------------------- |
| PostgreSQL | postgres:17.6             | 127.0.0.1:5432        | postgresql.{DOMAIN_NAME}:5432    | Database server         |
| Gitea      | gitea/gitea:1.24-rootless | 127.0.0.1:3000, :2222 | https://gitea.{DOMAIN_NAME}      | Git hosting (web + SSH) |
| pgAdmin    | dpage/pgadmin4:9.8.0      | 127.0.0.1:8081        | https://postgresql.{DOMAIN_NAME} | Database management UI  |

**Storage locations:**

- PostgreSQL data: `/srv/postgres/data`
- Gitea data: `/srv/gitea/data`, `/srv/gitea/config`
- pgAdmin data: `/srv/pgadmin/data`

### Network Services

| Service   | Purpose                                   | Port/Interface | Config Location                |
| --------- | ----------------------------------------- | -------------- | ------------------------------ |
| WireGuard | VPN server                                | 51820/UDP      | /etc/wireguard/wg0.conf        |
| Dnsmasq   | Internal DNS for custom domain            | 53 (on wg0)    | /etc/dnsmasq.conf              |
| NFTables  | Firewall (VPN and service access control) | -              | /etc/nftables.d/10-host-fw.nft |
| Nginx     | Reverse proxy with TLS termination        | 80, 443        | /etc/nginx/                    |
| Systemd   | Autostart orchestration                   | -              | /etc/systemd/system/           |

### VPN Network Layout

- **VPN Subnet:** 10.10.0.0/24
- **Server IP:** 10.10.0.1
- **Client IPs:** 10.10.0.2, 10.10.0.3, ...
- **DNS Server:** 10.10.0.1 (via split-DNS)

### Access Control

- **Gitea Web/SSH:** Accessible to all VPN clients
- **pgAdmin:** Restricted to first client only (10.10.0.2)
- **PostgreSQL Port 5432:** Restricted to specific clients (10.10.0.2, 10.10.0.3)
- All services bound to localhost, only accessible via VPN

## Usage

### First-Time Setup

1. **Build the tools:**

   ```bash
   ./build.sh
   ```

   This creates `.pyz` executables in `dist/`.

2. **Deploy to system:**

   ```bash
   sudo ./dist/self_deploy.pyz
   ```

   Copies tools to `/usr/local/sbin/` and data to `/usr/local/share/`.

3. **Install system packages:**

   ```bash
   sudo /usr/local/sbin/installer.pyz
   ```

4. **Configure services (interactive):**

   ```bash
   sudo /usr/local/sbin/configurator.pyz
   ```

   Answer prompts for all configuration variables. Settings are saved to `/usr/local/share/args/configuration_data.json`.

5. **Enable autostart:**

   ```bash
   sudo systemctl enable autostart.service
   sudo systemctl start autostart.service
   ```

6. **Distribute client files:**

   - Copy VPN configs from `{CLIENTS_DATA_DIR}/{client_name}.conf` to client devices
   - Import into WireGuard client application
   - Copy CA certificate from `{CLIENTS_DATA_DIR}/ca.crt`
   - Import CA cert into client OS trust store

7. **Connect and access services:**
   - Connect to VPN
   - Access Gitea: `https://gitea.{DOMAIN_NAME}`
   - Access pgAdmin: `https://postgresql.{DOMAIN_NAME}` (first client only)
   - Git over SSH: `ssh://git@gitea.{DOMAIN_NAME}:2222/username/repo.git`

### Re-configuration

To update settings, re-run the configurator:

```bash
sudo /usr/local/sbin/configurator.pyz
```

Previous values are loaded from `/usr/local/share/args/configuration_data.json` and can be modified.

### Manual Service Management

```bash
# Check service status
sudo systemctl status autostart.service
sudo docker compose -f /usr/local/share/{server_data_dir}/data/docker-compose.yml ps

# Restart services
sudo systemctl restart autostart.service

# View logs
sudo journalctl -u autostart.service -f
sudo docker logs -f gitea
```

## Security Notes

- All services bind to `127.0.0.1` (localhost only)
- External access only via WireGuard VPN
- NFTables firewall blocks all traffic except VPN and allowed services
- TLS encryption for all web traffic (internal CA)
- WireGuard provides encrypted VPN tunnel
- File permissions: WireGuard configs (0600), SSL keys (0600)

**Important:** Change all default passwords before deploying. Default credentials are for testing only.

## Project Structure

```
.
├── src/packages_engine/       # Core engine (commands, services, models)
├── tools/                     # Command entry points (installer, configurator, etc.)
├── data/                      # Configuration templates (docker-compose, nginx, etc.)
├── build.sh                   # Build script (creates .pyz zipapps)
├── dist/                      # Build output (.pyz files + data)
└── tests/                     # Unit tests
```

## License

MIT License - See project metadata for details.

## Author

For questions or issues, check the project repository.
