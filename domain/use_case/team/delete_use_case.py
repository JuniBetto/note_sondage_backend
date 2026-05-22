from datetime import datetime
from applications.dto.team.team_response_dto import TeamResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class DeleteTeamUseCase:
    def __init__(self, team_repository, notification_service: Notification):
        self.team_repository = team_repository
        self.notification_service = notification_service

    async def execute(self, team_id: str) -> TeamResponseDTO:
        team = await self.team_repository.find_by_id(team_id)
        if not team:
            raise ValueError("Team not found")

        deleted_team = await self.team_repository.delete(team_id)

        # Notifica dell'evento di eliminazione
        event_entity = EventEntity(
            name="Team Deleted",
            payload=deleted_team.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return TeamResponseDTO.from_entity(deleted_team)
