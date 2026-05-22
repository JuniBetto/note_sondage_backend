from domain.exceptions.other_exception import ConflictException, NotFoundException


class UserNotFound(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found")


class UserNotFoundByEmail(NotFoundException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' not found")


class UserAlreadyExists(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class UserInactive(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} is inactive")
