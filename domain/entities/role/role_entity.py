from uuid import UUID


class RoleEntity:
    def __init__(self, id: UUID, team_id: UUID, name: str, description: str):
        self.id = id
        self.team_id =team_id
        self.name = name
        self.description = description