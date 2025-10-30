# Server Management Tools Project

I had a need to set-up my own personal Linux Ubuntu home server. However, I also wanted to make it stable, easily configurable in cases something unexpected happens. On the other hand, I also wanted to keep the set-up as simple as possible. Another reason was to deepen my understanding about servers. And what is a better way to do so if not by introducing and managing your own personal home server? Thus, this is the reason why this Python project came into being.

Also, let me make one thing clear. All of the set-ups and configurations here are not guaranteed to be 100% secure, 100% working. It does not mean I do not try to make this insecure, but I want to explicitly say that this solution is not matured to the condition that can/should be used in environments where stability, scalability, security and other factors are of most importance. If you need those things, you should use other solutions instead of this one.

# Configuration and Current Variables

When configuring the server (i.e., using ./configure.pyz command), you will be asked to set some of the configuration values. To keep set-up faster for testing purposes, most of the configs have their default values if this makes any sense. It is not recommended to keep those defaults if you plan to use this script to set-up properly your own server.

## Server Data

| Configuration Key | Purpose                                                                                                                                                                                      | Default Value if Unset |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| SERVER_DATA_DIR   | Data directory where your files that come from this script will be deployed when using ./self-deploy.pyz command the first time server is installed and still needs to be accessed off-line. | srv                    |
| REMOTE_IP_ADDRESS | Your external IP address which is going to be used to connect to your server through the WireGuard VPN. To get it, you can use services like https://whatismyipaddress.com/                  | -                      |

## DNS

| Configuration Key | Purpose                                                                                                                                                                                                                                          | Default Value if Unset |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| DOMAIN_NAME       | Domain name that will be used when accessing internal server resources. E.g., if you server domain is internal.foo.example, then Gitea by clients that are connected to your VPN will be accessed like this: https://gitea.internal.foo.example/ | internal.app           |

## Gitea

| Configuration Key | Purpose                                                                               | Default Value if Unset |
| ----------------- | ------------------------------------------------------------------------------------- | ---------------------- |
| GITEA_DB_NAME     | Database name for the PostgreSQL database that is going to be used by Gitea.          | gitea                  |
| GITEA_DB_USER     | Database user for the PostgreSQL database that is going to be used by Gitea.          | gitea                  |
| GITEA_DB_PASSWORD | Database user password for the PostgreSQL database that is going to be used by Gitea. | 123456                 |
| GITEA_ADMIN_LOGIN | Gitea admin user name.                                                                | admin                  |
| GITEA_ADMIN_EMAIL | Gitea admin user email.                                                               | admin@example.com      |
| GITEA_DB_PASSWORD | Gitea admin user password.                                                            | 123456                 |
| GITEA_SECRET_KEY  | Gitea secret key.                                                                     | secret-key             |

## PostgreSQL

| Configuration Key | Purpose                                                        | Default Value if Unset |
| ----------------- | -------------------------------------------------------------- | ---------------------- |
| PG_ADMIN_EMAIL    | PostgreSQL admin email that you are going to use to log-in.    | user@example.com       |
| PG_ADMIN_PASSWORD | PostgreSQL admin password that you are going to use to log-in. | 123456                 |

## WireGuard

| Configuration Key | Purpose                                                                                                                                                                                                                                         | Default Value if Unset |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| SERVER_KEY        | Private key of the server that is going to be replaced with actual private key. It will be generated during the execution of configuration tasks, i.e., when executing ./configure.pyz command.                                                 | -                      |
| CLIENT_PUBLIC_KEY | Public key of the client that is going to be replaced with actual public key of the client that is connecting to the VPN. It will be generated during the execution of configuration tasks, i.e., when executing ./configure.pyz command.       | -                      |
| CLIENT_IP_ADDRESS | IP address of the client in the VPN that is going to be replaced with actual value of the client that is connecting to the VPN. It will be generated during the execution of configuration tasks, i.e., when executing ./configure.pyz command. | -                      |
