from applications.dto.team.team_response_dto import TeamResponseDTO


class FindTeamByIdUseCase:
    def __init__(self, team_repository):
        self.team_repository = team_repository

    async def execute(self, team_id: str) -> TeamResponseDTO | None:
        team = await self.team_repository.find_by_id(team_id)
        if not team:
            return None

        return TeamResponseDTO.from_entity(team)
