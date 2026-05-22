from datetime import datetime
from applications.dto.team_member.team_member_response_dto import TeamMemberResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class DeleteTeamMemberUseCase:
    def __init__(self, team_member_repository, notification_service: Notification):
        self.team_member_repository = team_member_repository
        self.notification_service = notification_service

    async def execute(self, member_id: str, member_email: str) -> TeamMemberResponseDTO:
        member = await self.team_member_repository.get_team_member_by_email(member_email)
        if not member:
            raise ValueError("Team member not found")

        deleted_member = await self.team_member_repository.delete_team_member(member_id)

        # Notifica dell'evento di eliminazione
        event_entity = EventEntity(
            name="Team Member Deleted",
            payload=deleted_member.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return TeamMemberResponseDTO.from_entity(deleted_member)
