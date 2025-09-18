from .input_collection_service_contract import InputCollectionServiceContract

class MockInputCollectionServiceContract(InputCollectionServiceContract):
    def __init__(self):
        self.read_str_params: list[str] = []
        self.read_str_result = ''
        self.read_int_params: list[str] = []
        self.read_int_result = 0
        
    def read_str(self, title: str) -> str:
        self.read_str_params.append(title)
        return self.read_str_result

    def read_int(self, title: str) -> int:
        self.read_int_params.append(title)
        return self.read_int_result