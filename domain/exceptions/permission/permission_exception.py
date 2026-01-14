from domain.exceptions.other_exception import ConflictException, NotFoundException


class PermissionNotFound(NotFoundException):
    def __init__(self, permission_id):
        super().__init__(f"Permission {permission_id} not found")


class PermissionAlreadyExists(ConflictException):
    def __init__(self, role: str):
        super().__init__(f"Permission with role '{role}' already exists")