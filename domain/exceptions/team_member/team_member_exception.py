from domain.exceptions.other_exception import ConflictException, NotFoundException


class TeamMemberNotFound(NotFoundException):
    def __init__(self, member_id: str):
        super().__init__(f"Team member {member_id} not found")


class TeamMemberNotFoundByEmail(NotFoundException):
    def __init__(self, email: str):
        super().__init__(f"Team member with email '{email}' not found")


class TeamMemberAlreadyExists(ConflictException):
    def __init__(self, user_email: str, team_id: str):
        super().__init__(f"User '{user_email}' is already a member of team {team_id}")


class TeamMemberSuspended(NotFoundException):
    def __init__(self, member_id: str):
        super().__init__(f"Team member {member_id} is suspended")
