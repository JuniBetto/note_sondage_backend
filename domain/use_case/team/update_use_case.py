from datetime import datetime
from applications.dto.team.team_request_dto import TeamRequestDTO, UpdateTeamRequestDTO
from applications.dto.team.team_response_dto import TeamResponseDTO, UpdateTeamResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.entities.team.team_entity import TeamEntityUpdated
from domain.exceptions.team.team_exception import TeamAlreadyExists


class UpdateTeamUseCase:
    def __init__(self, team_repository, notification_service: Notification):
        self.team_repository = team_repository
        self.notification_service = notification_service

    async def execute(self, team_id: str, dto: UpdateTeamRequestDTO) -> UpdateTeamResponseDTO:
        team = await self.team_repository.find_by_id(team_id)
        if not team:
            raise ValueError("Team not found")

        if dto.name is not None:
            team.name = dto.name
        if dto.color is not None:
            team.color = dto.color
        if dto.description is not None:
            team.description = dto.description
        if dto.name is not None and team.name != dto.name:
            if dto.name is not None and await self.team_repository.find_by_name_and_user_id(dto.name, team.created_by_user_id):
                raise TeamAlreadyExists(dto.name)


        

        # Crea TeamEntityUpdated con list_member dal DTO
        team_updated = TeamEntityUpdated(
            id=team.id,
            name=team.name,
            description=team.description,
            color=team.color,
            created_at=team.created_at,
            created_by_user_id=team.created_by_user_id,
            is_deleted=team.is_deleted,
            list_member=dto.list_member or []
        )

        updated_team = await self.team_repository.update(team_updated)

        # Notifica dell'evento di aggiornamento
        event_entity = EventEntity(
            name="Team Updated",
            payload=updated_team.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return UpdateTeamResponseDTO.from_entity(updated_team)
