from .notification_service_contract import NotificationsServiceContract

class MockNotificationsService(NotificationsServiceContract):
    params: list[object] = []

    def __init__(self):
        self.params = []
    
    def info(self, text: str):
        self.params.append({ 'type':'info', 'text': text })

    def error(self, text: str):
        self.params.append({ 'type':'error', 'text': text })

    def success(self, text: str):
        self.params.append({ 'type':'success', 'text': text })

    def warning(self, text: str):
        self.params.append({ 'type':'warning', 'text': text })