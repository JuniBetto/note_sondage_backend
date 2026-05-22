from applications.dto.team.team_response_dto import TeamResponseDTO


class GetAllTeamsUseCase:
    def __init__(self, team_repository):
        self.team_repository = team_repository

    async def execute(self) -> list[TeamResponseDTO]:
        teams = await self.team_repository.get_all()
        return [TeamResponseDTO.from_entity(team) for team in teams]
