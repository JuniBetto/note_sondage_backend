# domain/exceptions/domain_exception.py
class DomainException(Exception):
    code = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
