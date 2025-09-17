from .notification_service_contract import NotificationsServiceContract

class NotificationsService(NotificationsServiceContract):
    def info(self, text: str):
        print(f"{_Colors.OKBLUE}{text}{_Colors.ENDC}")

    def error(self, text: str):
        print(f"{_Colors.FAIL}{text}{_Colors.ENDC}")

    def success(self, text: str):
        print(f"{_Colors.OKGREEN}{text}{_Colors.ENDC}")

    def warning(self, text: str):
        print(f"{_Colors.WARNING}{text}{_Colors.ENDC}")

class _Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'