

from domain.exceptions.domain_exception import DomainException


class NotFoundException(DomainException):
    code = "NOT_FOUND"
    status_code = 404

class ConflictException(DomainException):
    code = "CONFLICT"
    status_code = 409