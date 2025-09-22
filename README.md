# Server Management Tools Project

I had a need to set-up my own personal Linux Ubuntu home server. However, I also wanted to make it stable, easily configurable in cases something unexpected happens. On the other hand, I also wanted to keep the set-up as simple as possible. Another reason was to deepen my understanding about servers. And what is a better way to do so if not by introducing and managing your own personal home server? Thus, this is the reason why this Python project came into being.

Also, let me make one thing clear. All of the set-ups and configurations here are not guaranteed to be 100% secure, 100% working. It does not mean I do not try to make this insecure, but I want to explicitly say that this solution is not matured to the condition that can/should be used in environments where stability, scalability, security and other factors are of most importance. If you need those things, you should use other solutions instead of this one.

# Configuration and Current Variables

When configuring the server (i.e., using ./configure.pyz command), you will be asked to set some of the configuration values. To keep set-up faster for testing purposes, most of the configs have their default values if this makes any sense. It is not recommended to keep those defaults if you plan to use this script to set-up properly your own server.

## Server Data

SERVER_DATA_DIR (default: srv)

## DNS

DOMAIN_NAME (default: internal.app)

## Gitea

GITEA_DB_NAME (default: gitea)
GITEA_DB_USER (default: gitea)
GITEA_DB_PASSWORD (default: 123456)

## PostgreSQL

PG_ADMIN_EMAIL (default: user@example.com)
PG_ADMIN_PASSWORD (default: 123456)

## WireGuard

SERVER_KEY (no default)
CLIENT_PUBLIC_KEY (no default)
CLIENT_IP_ADDRESS (no default)
