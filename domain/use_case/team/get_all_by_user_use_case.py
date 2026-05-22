from applications.dto.team.team_response_dto import TeamResponseDTO


class GetAllTeamsByUserUseCase:
    def __init__(self, user_id: str, team_repository,):
        self.user_id = user_id
        self.team_repository = team_repository

    async def execute(self) -> list[TeamResponseDTO] | None:
        """
        Ottiene tutte le squadre a cui un utente appartiene.
        :param user_id: ID dell'utente
        :return: Lista di squadre
        """  
        result = []

        data = await self.team_repository.get_all_by_user_id(self.user_id)
        if data is None:
            return []
        for team in data:
            result.append(TeamResponseDTO.from_entity(team))

        return result