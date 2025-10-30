"""Necessary imports."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfigurationData:
    """Configurations data model."""

    server_data_dir: str
    remote_ip_address: str
    domain_name: str
    gitea_db_name: str
    gitea_db_user: str
    gitea_db_password: str
    gitea_admin_login: str
    gitea_admin_email: str
    gitea_admin_password: str
    gitea_secret_key: str
    pg_admin_email: str
    pg_admin_password: str
    num_wireguard_clients: int
    wireguard_client_names: list[str]
    clients_data_dir: str

    @classmethod
    def default(cls):
        """Helper method to instantiate the data model easier."""
        return ConfigurationData(
            server_data_dir="",
            remote_ip_address="",
            domain_name="",
            gitea_db_name="",
            gitea_db_user="",
            gitea_db_password="",
            gitea_admin_login="",
            gitea_admin_email="",
            gitea_admin_password="",
            gitea_secret_key="",
            pg_admin_email="",
            pg_admin_password="",
            num_wireguard_clients=0,
            wireguard_client_names=[],
            clients_data_dir="",
        )

    def as_object(self) -> Any:
        """Converts class to object"""
        return {
            "server_data_dir": self.server_data_dir,
            "remote_ip_address": self.remote_ip_address,
            "domain_name": self.domain_name,
            "gitea_db_name": self.gitea_db_name,
            "gitea_db_user": self.gitea_db_user,
            "gitea_db_password": self.gitea_db_password,
            "gitea_admin_login": self.gitea_admin_login,
            "gitea_admin_email": self.gitea_admin_email,
            "gitea_admin_password": self.gitea_admin_password,
            "gitea_secret_key": self.gitea_secret_key,
            "pg_admin_email": self.pg_admin_email,
            "pg_admin_password": self.pg_admin_password,
            "num_wireguard_clients": self.num_wireguard_clients,
            "wireguard_client_names": self.wireguard_client_names,
            "clients_data_dir": self.clients_data_dir,
        }

    @classmethod
    def from_object(cls, obj: Any):
        """Converts object to the class"""
        data = ConfigurationData.default()
        data.server_data_dir = obj["server_data_dir"]
        data.remote_ip_address = obj["remote_ip_address"]
        data.domain_name = obj["domain_name"]
        data.gitea_db_name = obj["gitea_db_name"]
        data.gitea_db_user = obj["gitea_db_user"]
        data.gitea_db_password = obj["gitea_db_password"]
        data.gitea_admin_login = obj["gitea_admin_login"]
        data.gitea_admin_email = obj["gitea_admin_email"]
        data.gitea_admin_password = obj["gitea_admin_password"]
        data.gitea_secret_key = obj["gitea_secret_key"]
        data.pg_admin_email = obj["pg_admin_email"]
        data.pg_admin_password = obj["pg_admin_password"]
        data.num_wireguard_clients = obj["num_wireguard_clients"]
        data.wireguard_client_names = obj["wireguard_client_names"]
        data.clients_data_dir = obj["clients_data_dir"]
        return data
