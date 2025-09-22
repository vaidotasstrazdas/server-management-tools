from enum import Enum

class ConfigurationContent(Enum):
    RAW_STRING = 1
    WIREGUARD_SERVER_CONFIG = 2
    WIREGUARD_CLIENTS_CONFIG = 3