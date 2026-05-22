from domain.exceptions.other_exception import ConflictException, NotFoundException


class TeamNotFound(NotFoundException):
    def __init__(self, team_id: str):
        super().__init__(f"Team {team_id} not found")


class TeamAlreadyExists(ConflictException):
    def __init__(self, team_name: str):
        super().__init__(f"Team with name '{team_name}' already exists")


class TeamDeleted(NotFoundException):
    def __init__(self, team_id: str):
        super().__init__(f"Team {team_id} has been deleted")
