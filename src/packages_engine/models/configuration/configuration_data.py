"""Necessary imports."""

from dataclasses import dataclass


@dataclass
class ConfigurationData:
    """Configurations data model."""

    server_data_dir: str
    remote_ip_address: str
    domain_name: str
    gitea_db_name: str
    gitea_db_user: str
    gitea_db_password: str
    pg_admin_email: str
    pg_admin_password: str
    num_wireguard_clients: int
    wireguard_client_names: list[str]
    clients_data_dir: str

    @classmethod
    def default(cls):
        """Helper method to instantiate the data model easier."""
        return ConfigurationData("", "", "", "", "", "", "", "", 0, [], "")
