from domain.exceptions.other_exception import ConflictException, NotFoundException


class RoleNotFound(NotFoundException):
    def __init__(self, role_id: str):
        super().__init__(f"Role {role_id} not found")


class RoleAlreadyExists(ConflictException):
    def __init__(self, role_name: str):
        super().__init__(f"Role with name '{role_name}' already exists")


class RoleDeleted(NotFoundException):
    def __init__(self, role_id: str):
        super().__init__(f"Role {role_id} has been deleted")