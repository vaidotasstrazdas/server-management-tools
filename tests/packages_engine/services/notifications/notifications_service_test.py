import unittest
from unittest.mock import MagicMock, patch


from packages_engine.services.notifications import NotificationsService


package_name = 'packages_engine.services.notifications.notifications_service'

class TestNotificationsService(unittest.TestCase):
    service: NotificationsService

    def setUp(self):
        self.service = NotificationsService()
    
    @patch(f'{package_name}.print')
    def test_info_prints_correct_text(self, mock_run: MagicMock):

        # Act
        self.service.info('info message')

        # Assert
        mock_run.assert_called_once_with('\x1b[94minfo message\x1b[0m')
    
    @patch(f'{package_name}.print')
    def test_error_prints_correct_text(self, mock_run: MagicMock):

        # Act
        self.service.error('error message')

        # Assert
        mock_run.assert_called_once_with('\x1b[91merror message\x1b[0m')
    
    @patch(f'{package_name}.print')
    def test_success_prints_correct_text(self, mock_run: MagicMock):

        # Act
        self.service.success('success message')

        # Assert
        mock_run.assert_called_once_with('\x1b[92msuccess message\x1b[0m')
    
    @patch(f'{package_name}.print')
    def test_warning_prints_correct_text(self, mock_run: MagicMock):

        # Act
        self.service.warning('warning message')

        # Assert
        mock_run.assert_called_once_with('\x1b[93mwarning message\x1b[0m')

if __name__ == '__main__':
    unittest.main()