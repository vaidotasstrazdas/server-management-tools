from .input_collection_service_contract import InputCollectionServiceContract

class InputCollectionService(InputCollectionServiceContract):
    def read_str(self, title: str) -> str:
        read_str_input = input(f'{title.strip()}: ').strip()
        if read_str_input == '':
            print('Value is empty. Try again.')
            return self.read_str(title)
        
        return read_str_input

    def read_int(self, title: str) -> int:
        read_int_input = input(f'{title.strip()}: ').strip()
        if read_int_input == '':
            print('Value is empty. Try again.')
            return self.read_int(title)
        
        if not read_int_input.isdigit():
            print('Not a number. Try again.')
            return self.read_int(title)
        
        return int(read_int_input)