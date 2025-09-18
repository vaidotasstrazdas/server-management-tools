from typing import Optional, TypeVar

from .input_collection_service_contract import InputCollectionServiceContract

T = TypeVar('T')

class InputCollectionService(InputCollectionServiceContract):
    def read_str(self, title: str, default_value: Optional[str] = None) -> str:
        read_str_input = input(self._get_info(title, default_value)).strip()
        if read_str_input == '':
            if default_value != None:
                return default_value
            print('Value is empty. Try again.')
            return self.read_str(title, default_value)
        
        return read_str_input

    def read_int(self, title: str, default_value: Optional[int] = None) -> int:
        read_int_input = input(self._get_info(title, default_value)).strip()
        if read_int_input == '':
            if default_value != None:
                return default_value
            print('Value is empty. Try again.')
            return self.read_int(title, default_value)
        
        if not read_int_input.isdigit():
            print('Not a number. Try again.')
            return self.read_int(title, default_value)
        
        return int(read_int_input)
    
    def _get_info(self, title: str, default_value: Optional[T]) -> str:
        info = f'{title.strip()}'
        if default_value != None:
            info = f'{info} (click Enter to set default={default_value})'
        info = f'{info}: '
        return info