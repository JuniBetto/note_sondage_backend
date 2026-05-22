from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO


class GetAllTeamMembersByTeamUseCase:
    def __init__(self, team_member_repository, user_repository):
        self.team_member_repository = team_member_repository
        self.user_repository = user_repository

    async def execute(self, team_id: str) -> list[TeamMemberResponseDTO]:
        members = await self.team_member_repository.get_all_team_members_by_team_id(team_id)
        
        result = []
        for member in members:
            # Get user email
            user = await self.user_repository.find_by_id(member.user_id)
            user_email = user.email if user else ""
            try:
                result.append(TeamMemberResponseDTO.from_entity(member))
            except Exception as e:
                # Handle the exception (e.g., log it)
                print(f"Error converting team member to DTO: {str(e)}")

        return result
