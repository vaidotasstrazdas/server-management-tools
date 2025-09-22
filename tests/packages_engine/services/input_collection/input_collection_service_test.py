import unittest

from unittest.mock import call, MagicMock, Mock, patch
from packages_engine.services.input_collection import InputCollectionService

package_name = 'packages_engine.services.input_collection.input_collection_service'

class TestInputCollectionService(unittest.TestCase):
    service: InputCollectionService

    def setUp(self):
        self.service = InputCollectionService()
    
    @patch(f'{package_name}.input', Mock(return_value='value'))
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_str_happy_path(self):
        # Act
        result = self.service.read_str('Title')

        # Assert
        self.assertEqual(result, 'value')
    
    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_str_happy_path_input_makes_correct_calls(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            'value'
        ]

        # Act
        self.service.read_str('Title')

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call('Title: '),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print')
    def test_read_str_happy_path_print_makes_no_calls(self, mock_print: MagicMock, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            'value'
        ]

        mock_print.side_effect = [
            None
        ]

        # Act
        self.service.read_str('Title')

        # Assert
        mock_print.assert_not_called()

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print')
    def test_read_str_makes_necessary_print_calls_when_input_is_empty_or_white_space(self, mock_print: MagicMock, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            '  ',
            'value'
        ]

        mock_print.side_effect = [
            None,
            None
        ]

        # Act
        self.service.read_str('Title')

        # Assert
        mock_print.assert_has_calls(
            calls=[
                call('Value is empty. Try again.'),
                call('Value is empty. Try again.'),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_str_value_is_stripped(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '  value '
        ]

        # Act
        result = self.service.read_str('Title')

        # Assert
        self.assertEqual(result, 'value')
    
    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_str_input_makes_calls_as_many_times_as_value_is_empty_or_white_space(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            ' ',
            '',
            'value'
        ]

        # Act
        self.service.read_str('Title')

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call('Title: '),
                call('Title: '),
                call('Title: '),
                call('Title: '),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_str_empty_string_first(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            'value'
        ]

        # Act
        result = self.service.read_str('Title')

        # Assert
        self.assertEqual(result, 'value')
    
    @patch(f'{package_name}.input', Mock(return_value='10'))
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_int_happy_path(self):
        # Act
        result = self.service.read_int('Title')

        # Assert
        self.assertEqual(result, 10)
    
    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_int_happy_path_input_makes_correct_calls(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '10'
        ]

        # Act
        self.service.read_int('Title')

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call('Title: '),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print')
    def test_read_int_happy_path_print_makes_no_calls(self, mock_print: MagicMock, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '10'
        ]

        mock_print.side_effect = [
            None
        ]

        # Act
        self.service.read_int('Title')

        # Assert
        mock_print.assert_not_called()

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print')
    def test_read_int_makes_necessary_print_calls_when_input_is_empty_or_white_space(self, mock_print: MagicMock, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            '  ',
            '10'
        ]

        mock_print.side_effect = [
            None,
            None
        ]

        # Act
        self.service.read_int('Title')

        # Assert
        mock_print.assert_has_calls(
            calls=[
                call('Value is empty. Try again.'),
                call('Value is empty. Try again.'),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_int_value_is_stripped(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '  10 '
        ]

        # Act
        result = self.service.read_int('Title')

        # Assert
        self.assertEqual(result, 10)
    
    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_int_input_makes_calls_as_many_times_as_value_is_empty_or_white_space(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            ' ',
            '',
            '10'
        ]

        # Act
        self.service.read_int('Title')

        # Assert
        mock_input.assert_has_calls(
            calls=[
                call('Title: '),
                call('Title: '),
                call('Title: '),
                call('Title: '),
            ],
            any_order=False
        )

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print', Mock(return_value=None))
    def test_read_int_empty_string_first(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            '10'
        ]

        # Act
        result = self.service.read_int('Title')

        # Assert
        self.assertEqual(result, 10)

    @patch(f'{package_name}.input')
    @patch(f'{package_name}.print')
    def test_read_int_makes_necessary_print_calls_when_input_is_empty_white_space_or_invalid(self, mock_print: MagicMock, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
            'abc',
            '  ',
            '10'
        ]

        mock_print.side_effect = [
            None,
            None,
            None
        ]

        # Act
        self.service.read_int('Title')

        # Assert
        mock_print.assert_has_calls(
            calls=[
                call('Value is empty. Try again.'),
                call('Not a number. Try again.'),
                call('Value is empty. Try again.'),
            ],
            any_order=False
        )
    
    @patch(f'{package_name}.input')
    def test_read_int_default_value_is_returned_on_empty_string_when_default_value_provided(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
        ]

        # Act
        result = self.service.read_int('Title', 20)

        # Assert
        self.assertEqual(result, 20)
    
    @patch(f'{package_name}.input')
    def test_read_str_default_value_is_returned_on_empty_string_when_default_value_provided(self, mock_input: MagicMock):
        # Arrange
        mock_input.side_effect = [
            '',
        ]

        # Act
        result = self.service.read_str('Title', 'my default')

        # Assert
        self.assertEqual(result, 'my default')