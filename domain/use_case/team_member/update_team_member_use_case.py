from datetime import datetime
from applications.dto.team_member.team_member_request_dto import TeamMemberRequestDTO
from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class UpdateTeamMemberUseCase:
    def __init__(self, team_member_repository, notification_service: Notification):
        self.team_member_repository = team_member_repository
        self.notification_service = notification_service

    async def execute(self, member_email: str, dto: TeamMemberRequestDTO) -> TeamMemberResponseDTO:
        member = await self.team_member_repository.get_team_member_by_email(member_email)
        if not member:
            raise ValueError("Team member not found")

        if dto.status is not None:
            member.status = dto.status
        if dto.role_id is not None:
            member.role_id = dto.role_id
        if dto.image_url is not None:
            member.image_url = dto.image_url

        updated_member = await self.team_member_repository.update_team_member(member)

        # Notifica dell'evento di aggiornamento
        event_entity = EventEntity(
            name="Team Member Updated",
            payload=updated_member.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return TeamMemberResponseDTO.from_entity(updated_member)
