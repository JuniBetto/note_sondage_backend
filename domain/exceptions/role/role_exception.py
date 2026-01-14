from domain.exceptions.other_exception import ConflictException, NotFoundException


class RoleNotFound(NotFoundException):
    def __init__(self, Role_id):
        super().__init__(f"Role {Role_id} not found")


class RoleAlreadyExists(ConflictException):
    def __init__(self, role: str):
        super().__init__(f"Role with name '{role}' already exists")