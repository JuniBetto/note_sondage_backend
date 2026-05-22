from applications.dto.user.user_response_dto import UserFromTeamIdResponseDTO, UserResponseDTO


class FindUserByTeamIdUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def execute(self, team_id: str) -> list[UserFromTeamIdResponseDTO] | None:
        users = await self.user_repository.find_all_by_team_id(team_id)
        if not users:
            return None

        return [UserFromTeamIdResponseDTO.from_entity(user) for user in users]