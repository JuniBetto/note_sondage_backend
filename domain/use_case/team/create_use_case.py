from datetime import datetime
from uuid import uuid4
from applications.dto.team.team_request_dto import TeamRequestDTO
from applications.dto.team.team_response_dto import TeamResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.entities.team.team_entity import TeamEntity
from domain.exceptions.team.team_exception import TeamAlreadyExists


class CreateTeamUseCase:
    def __init__(self, team_repository, notification_service: Notification):
        self.team_repository = team_repository
        self.notification_service = notification_service

    async def execute(self, dto: TeamRequestDTO, created_by_user_id: str) -> TeamResponseDTO:
        # Create a new team entity
        team = TeamEntity(
            id=str(uuid4()),
            name=dto.name,
            color=dto.color,
            description=dto.description,
            created_at=datetime.now().isoformat(),
            created_by_user_id=created_by_user_id
        )

        if await self.team_repository.find_by_name_and_user_id(dto.name, created_by_user_id):
            raise TeamAlreadyExists(dto.name)
        # Save the team using the repository
        created_team = await self.team_repository.create(team)

        # Notifica dell'evento di creazione
        event_entity = EventEntity(
            name="Team Created",
            payload=created_team.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return TeamResponseDTO.from_entity(created_team)
