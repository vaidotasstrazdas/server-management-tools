"""Necessary imports"""

from packages_engine.models.configuration import ConfigurationData
from packages_engine.services.file_system import FileSystemServiceContract
from packages_engine.services.input_collection import InputCollectionServiceContract

from .configuration_data_reader_service_contract import ConfigurationDataReaderServiceContract


class ConfigurationDataReaderService(ConfigurationDataReaderServiceContract):
    """Configuration data reader service implementation."""

    def __init__(
        self,
        input_collection: InputCollectionServiceContract,
        file_system: FileSystemServiceContract,
    ):
        self.input_collection = input_collection
        self.file_system = file_system

    def read(self, stored: ConfigurationData | None = None) -> ConfigurationData:
        if not stored is None:
            option = self.input_collection.read_str(
                "You have stored configuration data. Type 'y' if you want to use stored data."
            ).strip()
            if option in ("y", "Y"):
                return stored

        data = ConfigurationData.default()

        data.server_data_dir = self.input_collection.read_str("Server data directory", "srv")
        data.remote_ip_address = self.input_collection.read_str("Remote Server IP Address")
        data.domain_name = self.input_collection.read_str("Domain name", "internal.app")
        data.gitea_db_name = self.input_collection.read_str("Gitea database name", "gitea")
        data.gitea_db_user = self.input_collection.read_str("Gitea database user", "gitea")
        data.gitea_db_password = self.input_collection.read_str("Gitea database password", "123456")
        data.pg_admin_email = self.input_collection.read_str(
            "PostgreSQL Admin Email", "user@example.com"
        )
        data.pg_admin_password = self.input_collection.read_str(
            "PostgreSQL Admin Password", "123456"
        )
        data.num_wireguard_clients = self.input_collection.read_int("Number of Server Clients", 2)

        wireguard_client_names: list[str] = []
        for num_cient in range(1, data.num_wireguard_clients + 1):
            client_name = self.input_collection.read_str(f"Name of the Server Client #{num_cient}")
            wireguard_client_names.append(client_name)

        data.wireguard_client_names = wireguard_client_names
        data.clients_data_dir = self.input_collection.read_str(
            "Mounted directory for the Clients Configuration"
        )

        self.file_system.write_json(
            "/usr/local/share/args/configuration_data.json", data.as_object()
        )

        return data

    def load_stored(self) -> ConfigurationData | None:
        read_result = self.file_system.read_json("/usr/local/share/args/configuration_data.json")
        if not read_result.success or read_result.data is None:
            return None

        data = read_result.data
        try:
            config_data = ConfigurationData.from_object(data)
            return config_data
        except KeyError:
            return None
