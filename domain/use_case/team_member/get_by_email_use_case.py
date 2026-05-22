from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO


class GetTeamMemberByEmailUseCase:
    def __init__(self, team_member_repository):
        self.team_member_repository = team_member_repository

    async def execute(self, email: str) -> TeamMemberResponseDTO | None:
        member = await self.team_member_repository.get_team_member_by_email(email)
        if not member:
            return None

        return TeamMemberResponseDTO.from_entity(member)
