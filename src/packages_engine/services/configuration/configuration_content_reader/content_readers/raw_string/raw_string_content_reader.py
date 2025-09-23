
from typing import Optional

from packages_engine.models.configuration import ConfigurationData
from packages_engine.models import OperationResult

from packages_engine.services.configuration.configuration_content_reader.content_readers import ContentReader
from packages_engine.services.file_system import FileSystemServiceContract

class RawStringContentReader(ContentReader):
    def __init__(self, file_system: FileSystemServiceContract):
        self.file_system = file_system

    def read(self, config: ConfigurationData, path: Optional[str] = None) -> OperationResult[str]:
        if path == None:
            return OperationResult[str].fail('Path cannot be empty')
        
        read_text_result = self.file_system.read_text(path)
        if not read_text_result.success or read_text_result.data == None:
            return read_text_result.as_fail()
        read_text_str = read_text_result.data

        result = read_text_str.replace('{{SERVER_DATA_DIR}}', config.server_data_dir)
        result = result.replace('{{DOMAIN_NAME}}', config.domain_name)
        result = result.replace('{{GITEA_DB_NAME}}', config.gitea_db_name)
        result = result.replace('{{GITEA_DB_USER}}', config.gitea_db_user)
        result = result.replace('{{GITEA_DB_PASSWORD}}', config.gitea_db_password)
        result = result.replace('{{PG_ADMIN_EMAIL}}', config.pg_admin_email)
        result = result.replace('{{PG_ADMIN_PASSWORD}}', config.pg_admin_password)

        return OperationResult[str].succeed(result)