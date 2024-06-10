class NoVATNumberFoundException(Exception):
    def __init__(self, vat_number: int):
        self.vat_number = vat_number

class NoNameFoundException(Exception):
    def __init__(self, name: str):
        self.name = name
